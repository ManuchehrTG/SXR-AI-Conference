from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class Subscription(BaseModel):
	id: int
	user_id: int
	offer: str
	status: str
	started_at: datetime
	expires_at: datetime
	updated_at: datetime

class SubscriptionStats(Subscription):
	username: str | None

	@property
	def started_at_str(self) -> str:
		return self.started_at.strftime("%Y-%m-%d %H:%M:%S")

	@property
	def expires_at_str(self) -> str:
		return self.expires_at.strftime("%Y-%m-%d %H:%M:%S")

	@property
	def updated_at_str(self) -> str:
		return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
