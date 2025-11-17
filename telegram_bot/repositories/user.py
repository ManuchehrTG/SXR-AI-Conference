from datetime import datetime
from typing import List

from infrastructure.database import db
from schemes.user import User, UserProfile

class UserRepository:
	@staticmethod
	async def create_or_update_user(user_id: int, first_name: str, username: str | None, language_code: str, is_admin: bool, source: str | None):
		record = await db.fetchrow(
			"""
			INSERT INTO users (id, first_name, username, language_code, is_admin, source)
			VALUES ($1, $2, $3, $4, $5, $6)
			ON CONFLICT (id) DO UPDATE SET
				first_name = EXCLUDED.first_name,
				username = EXCLUDED.username,
				language_code = EXCLUDED.language_code,
				is_admin = EXCLUDED.is_admin,
				updated_at = now()
			RETURNING *
			""",
			user_id,
			first_name,
			username,
			language_code,
			is_admin,
			source
		)
		return User(**record)

	@staticmethod
	async def get_by_id(user_id: int):
		record = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
		if record:
			return User(**record)

	@staticmethod
	async def get_users():
		records = await db.fetch("SELECT * FROM users")
		return [User(**record) for record in records]

	@staticmethod
	async def get_admins():
		records = await db.fetch("SELECT * FROM users WHERE is_admin = TRUE")
		return [User(**record) for record in records]

	@staticmethod
	async def update_user_profile(user: User, **kwargs):
		update_data = kwargs

		if not update_data:
			return user

		if UserProfile(**update_data) == UserProfile(**user.model_dump(include=UserProfile.model_fields)):
			return user

		set_clause = ", ".join(f"{key} = ${i+1}" for i, key in enumerate(update_data))
		values = list(update_data.values())
		values.append(user.id)  # для WHERE id = $N

		query = f"UPDATE users SET {set_clause} WHERE id = ${len(values)} RETURNING *"
		record = await db.fetchrow(query, *values)
		return User(**record)
