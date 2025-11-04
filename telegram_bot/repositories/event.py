import json
from datetime import datetime
from typing import List

from infrastructure.database import db
from schemes.event import EventType, Event, EventStats

class EventRepository:
	@staticmethod
	async def create_event(user_id: int, type: EventType, meta: dict | None = None) -> Event:
		if not meta:
			meta = {}

		meta = json.dumps(meta)

		record = await db.fetchrow(
			"""
			INSERT INTO events (user_id, type, meta)
			VALUES ($1, $2, $3)
			ON CONFLICT (user_id, type) DO UPDATE SET
				meta = events.meta
			RETURNING *
			""",
			user_id, type, meta
		)
		return Event(**record)

	@staticmethod
	async def get_user_events(user_id: int) -> List[Event]:
		records = await db.fetch("SELECT * FROM events WHERE user_id = $1", user_id)
		return [Event(**record) for record in records]

	@staticmethod
	async def get_stats_events() -> List[EventStats]:
		records = await db.fetch(
			"""
			SELECT
				e.*,
				u.username AS username
			FROM events e
			LEFT JOIN users u ON e.user_id = u.id
			"""
		)
		return [EventStats(**record) for record in records]
