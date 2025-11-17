from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Callable

class JobType(str, Enum):
	CRON = "cron"
	INTERVAL = "interval"
	DATE = "date"

class JobConfig(BaseModel):
	job_id: str
	func: Callable
	trigger_type: JobType
	args: list | None = None
	kwargs: dict | None = None
	start_date: datetime | None = None
	end_date: datetime | None = None

	# Для cron-триггера
	cron_expr: str | None = None

	# Для interval-триггера
	minutes: int = 0
	hours: int = 0
	days: int = 0

	timezone: str = "UTC"
