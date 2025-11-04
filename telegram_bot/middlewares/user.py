from aiogram import BaseMiddleware
from aiogram.filters import CommandObject
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Any, Awaitable, Callable, Dict

from configs import app_config, telegram_bot_config
from repositories.user import UserRepository
from schemes.user import User

class UserMiddleware(BaseMiddleware):
	def __init__(self, enable_create_user: bool = True) -> None:
		super().__init__()
		self.enable_create_user = enable_create_user

	async def __call__(
		self,
		handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: Dict[str, Any]
	) -> Any:
		user_id = event.from_user.id
		first_name = event.from_user.first_name
		username = event.from_user.username
		language_code = event.from_user.language_code

		if language_code not in app_config.LANGUAGES:
			language_code = app_config.DEFAULT_LANGUAGE

		is_admin = user_id in tuple(telegram_bot_config.ADMIN_IDS)

		source = await self._extract_source(event, data)

		if self.enable_create_user:
			user = await UserRepository.create_or_update_user(
				user_id=user_id,
				first_name=first_name,
				username=username,
				language_code=language_code,
				is_admin=is_admin,
				source=source
			)

			data["user"] = user
		else:
			data["user"] = User(
				id=user_id,
				first_name=first_name,
				username=username,
				language_code=language_code,
				is_admin=is_admin
			)

		return await handler(event, data)

	async def _extract_source(self, event: TelegramObject, data: Dict[str, Any]) -> str | None:
		if isinstance(event, Message) and event.text and event.text.startswith('/start'):
			try:
				command: CommandObject = data.get("command")
				if command and command.args:
					return command.args

			except Exception as e:
				logger.error(f"Error parsing UTM parameters: {e}")
