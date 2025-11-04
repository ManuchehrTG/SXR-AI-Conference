from aiogram import Bot

from configs import telegram_bot_config
from keyboards.offers import OffersInlineKeyboard
from repositories.subscription import SubscriptionRepository
from services.payment import PaymentService
from schemes.user import User
from utils.i18n import i18n

async def offer_payment(bot: Bot, user: User):
	offer = "club"
	value = telegram_bot_config.CLUB_VALUE
	quantity = telegram_bot_config.CLUB_QUANTITY

	offer_locale = i18n.translate(namespace=f"offers.{offer}", lang=user.language_code)

	subscription = await SubscriptionRepository.get_by_user_id_and_offer_and_status(user_id=user.id, offer=offer, status="active")
	if subscription:
		text = offer_locale["errors"]["subscription_exists"]["message"]
		reply_markup = OffersInlineKeyboard.manager(manager_url=f"https://t.me/{telegram_bot_config.MANAGER_USERNAME}")
		return await bot.send_message(chat_id=user.id, text=text, reply_markup=reply_markup)

	subscription = await SubscriptionRepository.get_by_user_id_and_offer_and_status(user_id=user.id, offer=offer, status="inactive")

	if not subscription:
		metadata ={"days": 90, "method": "initial"}
		text = offer_locale["payment"]["month3"]["message"].format(privacy_url=telegram_bot_config.PRIVACY_URL)
	else:
		text = offer_locale["payment"]["month1"]["message"].format(privacy_url=telegram_bot_config.PRIVACY_URL)
		metadata = {"days": 30, "method": "renewal", "subscription_id": subscription.id}

	payment_url = await PaymentService.create_payment(
		user=user,
		offer=offer,
		type="subscription",
		value=value,
		quantity=quantity,
		metadata=metadata
	)

	reply_markup = OffersInlineKeyboard.payment(payment_url=payment_url)
	await bot.send_message(chat_id=user.id, text=text, reply_markup=reply_markup)
