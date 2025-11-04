import json
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, field_validator, field_serializer
from types import SimpleNamespace
from uuid import UUID

class Transaction(BaseModel):
	id: UUID
	user_id: int
	offer: str
	type: str
	provider_tx_id: str
	provider_payload: dict
	status: str
	created_at: datetime
	updated_at: datetime

	@staticmethod
	def _dict_to_ns(data):
		if isinstance(data, dict):
			return SimpleNamespace(**{k: Transaction._dict_to_ns(v) for k, v in data.items()})
		elif isinstance(data, list):
			return [Transaction._dict_to_ns(i) for i in data]
		return data

	@property
	def provider_payload_obj(self):
		return self._dict_to_ns(self.provider_payload)

	@field_validator("provider_payload", mode="before")
	@classmethod
	def provider_parse_payload(cls, value):
		if isinstance(value, str):
			return json.loads(value)
		return value

	@field_serializer("provider_payload")
	def provider_serialize_payload(self, value: dict) -> str:
		return json.dumps(value)

class TransactionOfferType(str, Enum):
	COURSE = "course"
	CLUB = "club"

class TransactionType(str, Enum):
	SUBSCRIPTION = "subscription"
	PRODUCT = "product"

class TransactionStatusType(str, Enum):
	PENDING = "pending"
	SUCCEEDED = "succeeded"
	CANCELED = "canceled"
