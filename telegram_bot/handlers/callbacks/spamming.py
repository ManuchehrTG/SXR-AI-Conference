import json
import uuid
from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from celery_app.tasks.send_telegram import send_telegram
from filters.users import IsAdminFilter
from infrastructure.redis import redis
from keyboards import BaseCallbackData
from keyboards.spamming import SpammingCallbackData, SpammingReplyKeyboard
from repositories.user import UserRepository
from schemes.user import User
from states.admin import StateSpamming
from utils.i18n import i18n
from utils.telegram import MediaProcessing, SafeMessage

router = Router()

@router.callback_query(F.message.chat.type == "private", BaseCallbackData.filter((F.role == "admin") & (F.action == "spamming")), IsAdminFilter())
async def handle_spamming(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)
	await state.set_state(StateSpamming.post)
	await call.message.answer(
		text=i18n.translate(namespace="responses.spamming", key="message", lang=user.language_code),
		reply_markup=SpammingReplyKeyboard.cancel()
	)

@router.callback_query(
	F.message.chat.type == "private",
	SpammingCallbackData.filter((F.role == "admin") & (F.action == "preview")),
	StateSpamming.settings,
	IsAdminFilter()
)
async def handle_preview(call: CallbackQuery, callback_data: SpammingCallbackData, state: FSMContext, bot: Bot, user: User):
	data_state = await state.get_data()

	await call.answer()
	if data_state.get("media_json"):
		media = MediaProcessing.pack(media_files=data_state["media_json"])
		await call.message.answer_media_group(media=media)
	else:
		await call.message.answer(text=data_state["text"])

@router.callback_query(
	F.message.chat.type == "private",
	SpammingCallbackData.filter((F.role == "admin") & (F.action == "edit_post")),
	StateSpamming.settings,
	IsAdminFilter()
)
async def handle_edit_post(call: CallbackQuery, callback_data: SpammingCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)
	await state.set_state(StateSpamming.edit_post)
	await call.message.answer(
		text=i18n.translate(namespace="responses.spamming", key="editing.message", lang=user.language_code),
		reply_markup=SpammingReplyKeyboard.cancel()
	)

@router.callback_query(
	F.message.chat.type == "private",
	SpammingCallbackData.filter((F.role == "admin") & (F.action == "run")),
	StateSpamming.settings,
	IsAdminFilter()
)
async def handle_run(call: CallbackQuery, callback_data: SpammingCallbackData, state: FSMContext, bot: Bot, user: User):
	spamming_locale = i18n.translate(namespace="responses.spamming", lang=user.language_code)

	is_running = await redis.set("spamming_is_running", "1", nx=True)
	if not is_running:
		text = spamming_locale["errors"]["spamming_is_running"]["message"]
		return await call.answer(text=text, show_alert=True)

	data_state = await state.get_data()
	await state.clear()

	users = await UserRepository.get_users()
	total_users = len(users)
	spamming_id = str(uuid.uuid4())

	text = spamming_locale["run"]["message"].format(
		total_users=total_users,
		spamming_id=spamming_id
	)

	await SafeMessage.message_delete(message=call.message)
	await call.message.answer(text=text)

	if data_state.get("media_json"):
		content_type = "media_group"
		payload_kwargs = {"media": json.dumps(data_state["media_json"])}
	else:
		content_type = "text"
		payload_kwargs = {"text": data_state["text"], "parse_mode": "HTML"}

	await redis.hset(f"spamming_id:{spamming_id}", mapping={
		"total": total_users,
		"processed": 0,
		"successful": 0,
		"failed": 0
	})

	for u in users:
		send_telegram.delay(spamming_id=spamming_id, user_id=u.id, content_type=content_type, **payload_kwargs)
