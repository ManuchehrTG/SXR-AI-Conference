import json
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, field_serializer
from types import SimpleNamespace

class EventType(str, Enum):
	SUB_OK = "sub_ok"
	STUDIO_COUPON_ISSUED = "studio_coupon_issued"
	COURSE_PROMOCODES_ISSUED = "course_promocodes_issued"
	CLUB_PAID = "club_paid"
	INVITE_ISSUED = "invite_issued"

	CLICK_STUDIO = "click_studio"
	CLICK_COURSE = "click_course"
	CLICK_CLUB = "click_club"

class Event(BaseModel):
	id: int
	user_id: int
	type: EventType
	meta: dict = Field(default_factory=dict)
	ts: datetime

	@staticmethod
	def _dict_to_ns(data):
		if isinstance(data, dict):
			return SimpleNamespace(**{k: Event._dict_to_ns(v) for k, v in data.items()})
		elif isinstance(data, list):
			return [Event._dict_to_ns(i) for i in data]
		return data

	@property
	def meta_obj(self):
		return self._dict_to_ns(self.meta)

	@field_validator("meta", mode="before")
	@classmethod
	def provider_parse_payload(cls, value):
		if isinstance(value, str):
			return json.loads(value)
		return value

	@field_serializer("meta")
	def provider_serialize_payload(self, value: dict) -> str:
		return json.dumps(value)

class EventStats(Event):
	username: str | None

	@property
	def ts_str(self) -> str:
		return self.ts.strftime("%Y-%m-%d %H:%M:%S")
