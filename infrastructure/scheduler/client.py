from abc import ABC, abstractmethod

from .models import JobConfig

class SchedulerClient(ABC):
	@abstractmethod
	async def add_job(self, config: JobConfig) -> str: ...

	@abstractmethod
	async def remove_job(self, job_id: str) -> bool: ...

	@abstractmethod
	async def pause_job(self, job_id: str) -> None: ...

	@abstractmethod
	async def resume_job(self, job_id: str) -> None: ...

	@abstractmethod
	async def get_jobs(self) -> list[dict]: ...
