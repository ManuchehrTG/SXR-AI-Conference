from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from configs import telegram_bot_config
from keyboards.templates import TemplatesInlineKeyboard
from keyboards.offers import OfferCallbackData, OffersInlineKeyboard
from repositories.user import UserRepository
from repositories.event import EventRepository
from schemes.user import User
from states.user import StateEmail
from use_cases.chat_member import get_chat_member
from use_cases.offer_payment import offer_payment
from utils.i18n import i18n
from utils.telegram import SafeMessage

router = Router()

@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "main_menu")), StateFilter(None))
async def handle_back_to_main_menu(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await state.clear()

	await SafeMessage.message_delete(message=call.message)

	text = i18n.translate(namespace="commands.start", key="message", lang=user.language_code)
	reply_markup = OffersInlineKeyboard.offers()
	await call.message.answer(text=text, reply_markup=reply_markup)


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "offer_studio")))
async def handle_offer_studo(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	text = i18n.translate(namespace="offers.studio", key="message", lang=user.language_code)
	reply_markup = OffersInlineKeyboard.studio(channel_url=telegram_bot_config.STUDIO_CHANNEL_URL)
	await call.message.answer(text=text, reply_markup=reply_markup)
	await EventRepository.create_event(user_id=user.id, type="click_studio")


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "offer_ozon_tables")))
async def handle_offer_ozon_tables(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	text = i18n.translate(namespace="offers.ozon_tables", key="message", lang=user.language_code)
	reply_markup = OffersInlineKeyboard.ozon_tables(channel_url=telegram_bot_config.OZON_TABLES_CHANNEL_URL)
	await call.message.answer(text=text, reply_markup=reply_markup)


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "check_sub")))
async def handle_check_sub(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):

	offer = callback_data.target
	offer_locale = i18n.translate(namespace=f"offers.{offer}", lang=user.language_code)

	if offer == "studio":
		channel_id = telegram_bot_config.STUDIO_CHANNEL_ID
	elif offer == "ozon_tables":
		channel_id = telegram_bot_config.OZON_TABLES_CHANNEL_ID

	member = await get_chat_member(bot, channel_id, user.id)
	if not (member and member.status in ("member", "administrator", "creator")):
		text = offer_locale["errors"]["user_not_in_chat"]["message"]
		return await call.message.answer(text=text)

	await SafeMessage.message_delete(message=call.message)

	if offer == "studio":
		if user.studio_coupon_used:
			text = offer_locale["errors"]["coupon_already_activated"]["message"].format(coupon=telegram_bot_config.STUDIO_COUPON)
			return await call.message.answer(text=text)

		await UserRepository.update_user_profile(user=user, studio_coupon_used=True)
		await EventRepository.create_event(user_id=user.id, type="sub_ok")

		text = offer_locale["success"]["message"].format(coupon=telegram_bot_config.STUDIO_COUPON)
		reply_markup = OffersInlineKeyboard.studio_success(studio_open_chat_link=telegram_bot_config.STUDIO_OPEN_CHAT_LINK)

	elif offer == "ozon_tables":
		text = offer_locale["success"]["message"]
		reply_markup = OffersInlineKeyboard.ozon_tables_success(ozon_tables_post_url=telegram_bot_config.OZON_TABLES_POST_URL)

	await call.message.answer(text=text, reply_markup=reply_markup)
	await EventRepository.create_event(user_id=user.id, type="studio_coupon_issued")


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "offer_course")))
async def handle_offer_course(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	text = i18n.translate(namespace="offers.course", key="message", lang=user.language_code)
	reply_markup = OffersInlineKeyboard.course(course_telegraph_url=telegram_bot_config.COURSE_TELEGRAPH_URL)

	await call.message.answer(text=text, reply_markup=reply_markup)
	await EventRepository.create_event(user_id=user.id, type="click_course")


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "course_promocodes")))
async def handle_offer_course_promocodes(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	text = i18n.translate(namespace="offers.course", key="success.message", lang=user.language_code).format(
		course_promocode_vip=telegram_bot_config.COURSE_PROMOCODE_VIP
	)
	reply_markup = OffersInlineKeyboard.course_success(course_url=telegram_bot_config.COURSE_URL)

	await call.message.answer(text=text, reply_markup=reply_markup)
	await EventRepository.create_event(user_id=user.id, type="course_promocodes_issued")


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "offer_club")))
async def handle_offer_club(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	text = i18n.translate(namespace="offers.club", key="message", lang=user.language_code)
	reply_markup = OffersInlineKeyboard.club(club_info_url=telegram_bot_config.CLUB_INFO_URL)

	await call.message.answer(text=text, reply_markup=reply_markup)
	await EventRepository.create_event(user_id=user.id, type="click_club")


@router.callback_query(F.message.chat.type == "private", OfferCallbackData.filter((F.role == "user") & (F.action == "pay_club")))
async def handle_offer_pay_club(call: CallbackQuery, callback_data: OfferCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	if not user.agreed_privacy:
		text = i18n.translate(namespace="responses.privacy", key="message", lang=user.language_code).format(
			privacy_url=telegram_bot_config.PRIVACY_URL
		)
		reply_markup = TemplatesInlineKeyboard.privacy(privacy_url=telegram_bot_config.PRIVACY_URL)
		return await call.message.answer(text=text, reply_markup=reply_markup, disable_web_page_preview=True)
	elif not user.email:
		await state.set_state(StateEmail.email)
		text = i18n.translate(namespace="responses.email", key="message", lang=user.language_code)
		return await call.message.answer(text=text, reply_markup=reply_markup)

	await offer_payment(bot=bot, user=user)
