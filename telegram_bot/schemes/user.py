from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
	id: int
	first_name: str
	username: str | None
	language_code: str
	email: str | None
	agreed_privacy: bool
	studio_coupon_used: bool
	is_admin: bool
	source: str | None
	created_at: datetime
	updated_at: datetime

	@property
	def created_at_str(self) -> str:
		return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

	@property
	def updated_at_str(self) -> str:
		return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

class UserProfile(BaseModel):
	language_code: str | None = None
	email: str | None = None
	agreed_privacy: bool = False
	studio_coupon_used: bool = False
	is_admin: bool = False
