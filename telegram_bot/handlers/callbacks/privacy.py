from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards import BaseCallbackData
from schemes.user import User
from repositories.user import UserRepository
from states.user import StateEmail
from use_cases.offer_payment import offer_payment
from utils.i18n import i18n
from utils.telegram import SafeMessage

router = Router()

@router.callback_query(F.message.chat.type == "private", BaseCallbackData.filter((F.role == "user") & (F.action == "accept_privacy")), StateFilter(None))
async def handle_accept_privacy(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)

	reply_markup = None

	if not user.agreed_privacy:
		await UserRepository.update_user_profile(user=user, agreed_privacy=True)

	if not user.email:
		await state.set_state(StateEmail.email)
		text = i18n.translate(namespace="responses.email", key="message", lang=user.language_code)
		return await call.message.answer(text=text, reply_markup=reply_markup)

	await offer_payment(bot=bot, user=user)
