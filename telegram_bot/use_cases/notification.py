import json
from aiogram import Bot
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from configs import app_config, telegram_bot_config
from celery_app.tasks.send_notification import send_notification
from infrastructure.logger import logger
from infrastructure.redis import redis
from keyboards.offers import OffersInlineKeyboard
from repositories.user import UserRepository
from repositories.subscription import SubscriptionRepository
from services.payment import PaymentService
from utils.i18n import i18n
from .chat_member import kick_chat_member

async def payment_notification():
	days_left = 5

	tz_moscow = ZoneInfo(app_config.TIME_ZONE)
	now_msk = datetime.now(tz=tz_moscow)
	today_noon_msk = now_msk.replace(hour=12, minute=0, second=0, microsecond=0)

	today_noon_utc = today_noon_msk.astimezone(timezone.utc)
	target_date_utc = today_noon_utc + timedelta(days=days_left)

	subscriptions = await SubscriptionRepository.get_expiring_subscriptions(expires_at=target_date_utc)

	for sub in subscriptions:
		user = await UserRepository.get_by_id(user_id=sub.user_id)

		payment_url = await PaymentService.create_payment(
			user=user,
			offer=sub.offer,
			type="subscription",
			value=telegram_bot_config.CLUB_VALUE,
			quantity=telegram_bot_config.CLUB_QUANTITY,
			metadata={"days": 30, "method": "renewal", "subscription_id": sub.id}
		)

		text = i18n.translate(namespace="offers.club", key="notification.subscription_ends.message", lang=user.language_code)
		reply_markup = OffersInlineKeyboard.payment(payment_url=payment_url, show_btn_back=False)

		send_notification.delay(user_id=user.id, text=text, reply_markup=json.dumps(reply_markup.model_dump()))

async def kick_user_notification(bot: Bot):
	subscriptions = await SubscriptionRepository.get_expired_subscriptions()

	for sub in subscriptions:
		user = await UserRepository.get_by_id(user_id=sub.user_id)
		await SubscriptionRepository.update_subscription_status(subscription_id=sub.id, status="inactive")
		flag = await kick_chat_member(bot=bot, chat_id=telegram_bot_config.CLUB_CHAT_ID, user_id=sub.user_id)

		if flag:
			# text = i18n.translate(namespace="offers.club", key="notification.subscription_ends.message", lang=user.language_code)
			# reply_markup = OffersInlineKeyboard.payment(payment_url=payment_url, show_btn_back=False)
			# send_notification.delay(user_id=user.id, text=text, reply_markup=json.dumps(reply_markup.model_dump()))

			text = "Ваша подписка истечена!"
			send_notification.delay(user_id=user.id, text=text)


async def check_spamming(bot: Bot):
	keys = await redis.keys(f"spamming_id:*")
	for key in keys:
		data_raw = await redis.hgetall(key)
		data = {k.decode(): v.decode() for k, v in data_raw.items()}

		if not data:
			continue

		total = int(data.get("total", 0))
		processed = int(data.get("processed", 0))

		spamming_id = key.decode().replace("spamming_id:", "")

		successful = int(data.get("successful", 0))
		failed = int(data.get("failed", 0))

		if total != processed:
			continue

		admins = await UserRepository.get_admins()

		for admin in admins:
			try:
				text = i18n.translate(namespace="responses.spamming", key="results.message", lang=admin.language_code).format(
					spamming_id=spamming_id,
					total=total,
					successful=successful,
					failed=failed
				)
				await bot.send_message(chat_id=admin.id, text=text)
			except Exception as e:
				logger.error(f"Failed to send notification [SpammingResults] to admin {admin.id}: {e}")

		await redis.delete(key)
		await redis.delete("spamming_is_running")
