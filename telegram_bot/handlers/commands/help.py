from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from configs import telegram_bot_config
from schemes.user import User
from utils.i18n import i18n

router = Router()

@router.message(Command("help"), F.chat.type == "private")
async def command_help(message: Message, state: FSMContext, bot: Bot, user: User):
	await state.clear()

	text = i18n.translate(namespace="commands.help", key="message", lang=user.language_code).format(support_username=telegram_bot_config.MANAGER_USERNAME)

	await message.answer(text=text, disable_web_page_preview=True)

