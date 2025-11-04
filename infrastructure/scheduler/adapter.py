from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from typing import Any, List
from zoneinfo import ZoneInfo

from .models import JobConfig, JobType
from .client import SchedulerClient

class APSchedulerAdapter(SchedulerClient):
	def __init__(self):
		self.scheduler = AsyncIOScheduler(timezone=ZoneInfo("UTC"))
		self.jobstore = "default"  # Можно заменить на RedisJobStore

	async def start(self) -> None:
		self.scheduler.start()

	async def shutdown(self) -> None:
		self.scheduler.shutdown()

	async def add_job(self, config: JobConfig) -> str:
		trigger = self._create_trigger(config)
		job = self.scheduler.add_job(
			config.func,
			trigger=trigger,
			args=config.args,
			kwargs=config.kwargs,
			id=config.job_id,
			start_date=config.start_date,
			end_date=config.end_date,
		)
		return job.id

	def _create_trigger(self, config: JobConfig) -> Any:
		tz = ZoneInfo(config.timezone) if config.timezone else None

		if config.trigger_type == JobType.CRON:
			return CronTrigger.from_crontab(config.cron_expr, timezone=tz)
		elif config.trigger_type == JobType.INTERVAL:
			return IntervalTrigger(minutes=config.minutes, hours=config.hours, days=config.days, timezone=tz)
		elif config.trigger_type == JobType.DATE:
			return DateTrigger(run_date=config.start_date, timezone=tz)
		raise ValueError(f"Unknown trigger type: {config.trigger_type}")

	async def remove_job(self, job_id: str) -> bool:
		return bool(self.scheduler.remove_job(job_id))

	async def pause_job(self, job_id: str) -> None:
		self.scheduler.pause_job(job_id)

	async def resume_job(self, job_id: str) -> None:
		self.scheduler.resume_job(job_id)

	async def get_jobs(self) -> List[dict]:
		return [{"id": job.id, "name": job.name} for job in self.scheduler.get_jobs()]
