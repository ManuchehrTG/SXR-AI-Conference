from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from configs import telegram_bot_config
from repositories.subscription import SubscriptionRepository
from repositories.event import EventRepository
from schemes.user import User
from schemes.event import EventType
from utils.i18n import i18n

router = Router()

@router.message(Command("status"), F.chat.type == "private")
async def command_status(message: Message, state: FSMContext, bot: Bot, user: User):
	await state.clear()

	subscription = await SubscriptionRepository.get_by_user_id_and_offer_and_status(user_id=user.id, offer="club", status="active")
	events = await EventRepository.get_user_events(user_id=user.id)

	coupons_list = []
	for event in events:
		if event.type == EventType.STUDIO_COUPON_ISSUED:
			coupons_list.append(telegram_bot_config.STUDIO_COUPON)

	coupons_str = "Отсутствуют"
	if coupons_list:
		coupons_str = ", ".join(f"<code>{coupon}</code>" for coupon in coupons_list)

	text = i18n.translate(namespace="commands.status", key="message", lang=user.language_code).format(
		has_subscription=True if subscription else False,
		coupons_str=coupons_str
	)

	await message.answer(text=text, disable_web_page_preview=True)
