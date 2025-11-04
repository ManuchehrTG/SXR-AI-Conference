from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from email_validator import validate_email, EmailNotValidError

from repositories.user import UserRepository
from schemes.user import User
from states.user import StateEmail
from use_cases.offer_payment import offer_payment
from utils.i18n import i18n

router = Router()

@router.message(F.chat.type == "private", F.text, StateEmail.email)
async def message_email(message: Message, state: FSMContext, bot: Bot, user: User):
	try:
		valid = validate_email(message.text.strip())
		email = valid.email
	except EmailNotValidError as e:
		text = i18n.translate(namespace="responses.email", key="errors.invalid.message", lang=user.language_code)
		return await message.answer(text=text)

	user = await UserRepository.update_user_profile(user=user, email=email)

	await state.clear()
	await offer_payment(bot=bot, user=user)
