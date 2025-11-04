import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from configs import app_config, telegram_bot_config
from core.container import container
from keyboards.offers import OffersInlineKeyboard
from repositories.user import UserRepository
from repositories.subscription import SubscriptionRepository
from repositories.event import EventRepository
from schemes.transaction import Transaction
from utils.i18n import i18n

class OfferService:
	@staticmethod
	async def handle_successful_payment(transaction: Transaction):
		user = await UserRepository.get_by_id(user_id=transaction.user_id)
		bot = container.bot

		payment = transaction.provider_payload_obj
		payment_method = payment.metadata.method

		tz_moscow = ZoneInfo(app_config.TIME_ZONE)
		now_msk = datetime.now(tz=tz_moscow).replace(hour=12, minute=0, second=0, microsecond=0)
		start_date = now_msk.astimezone(timezone.utc)
		end_date = start_date + timedelta(days=int(payment.metadata.days))

		offer_club_locale = i18n.translate(namespace="offers.club", lang=user.language_code)

		if payment_method == "initial":
			subscription = await SubscriptionRepository.create_subscription(
				user_id=user.id,
				offer=transaction.offer,
				started_at=start_date,
				expires_at=end_date
			)
			await SubscriptionRepository.create_subscription_transaction(subscription_id=subscription.id, transaction_id=transaction.id, type=payment_method)
		elif payment_method == "renewal":
			subscription = await SubscriptionRepository.update_subscription(
				subscription_id=int(payment.metadata.subscription_id),
				add_days=int(payment.metadata.days)
			)
			await SubscriptionRepository.create_subscription_transaction(subscription_id=subscription.id, transaction_id=transaction.id, type=payment_method)
			text = offer_club_locale["extended"]["message"].format(
				expires_at_str=subscription.expires_at.strftime("%d.%m.%Y")
			)
			return await bot.send_message(chat_id=user.id, text=text)

		await EventRepository.create_event(user_id=user.id, type="club_paid")

		try:
			invite_link = await bot.create_chat_invite_link(
				chat_id=telegram_bot_config.CLUB_CHAT_ID,
				expire_date=int(time.time()) + 48 * 3600,
				member_limit=1
			)
			await EventRepository.create_event(user_id=user.id, type="invite_issued")
		except Exception as e:
			text = offer_club_locale["errors"]["error_create_invite_link"]["message"]
			reply_markup = OffersInlineKeyboard.manager(manager_url=f"https://t.me/{telegram_bot_config.MANAGER_USERNAME}")
			return await bot.send_message(chat_id=user.id, text=text, reply_markup=reply_markup)

		text = offer_club_locale["success"]["message"]
		reply_markup = OffersInlineKeyboard.club_success(invite_link=invite_link.invite_link)

		await bot.send_message(chat_id=user.id, text=text, reply_markup=reply_markup)
