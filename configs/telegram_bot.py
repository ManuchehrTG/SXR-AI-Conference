from decimal import Decimal
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List

class TelegramBotConfig(BaseSettings):
	TOKEN: str
	ADMIN_IDS: List[int] = Field(default_factory=list)
	SUPPORT_USERNAME: str

	PORT: int
	DOMAIN: str

	MANAGER_USERNAME: str

	PRIVACY_URL: str

	STUDIO_CHANNEL_ID: int
	STUDIO_CHANNEL_URL: str
	STUDIO_OPEN_CHAT_LINK: str
	STUDIO_COUPON: str

	OZON_TABLES_CHANNEL_ID: int
	OZON_TABLES_CHANNEL_URL: str
	OZON_TABLES_POST_URL: str

	COURSE_TELEGRAPH_URL: str
	COURSE_URL: str
	COURSE_PROMOCODE_VIP: str

	CLUB_CHAT_ID: int
	CLUB_INFO_URL: str
	CLUB_VALUE: Decimal
	CLUB_QUANTITY: Decimal

	class Config:
		env_prefix = "TELEGRAM_BOT_"

telegram_bot_config = TelegramBotConfig()
