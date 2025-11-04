from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from configs import telegram_bot_config
from filters.users import IsAdminFilter
from repositories.user import UserRepository
from repositories.subscription import SubscriptionRepository
from repositories.event import EventRepository
from repositories.analytics import AnalyticsRepository
from schemes.user import User
from utils.i18n import i18n
from utils.excel.export_tables import save_to_excel

router = Router()

def calculate_conversion_stats(offer_analytics, total_users):
	for offer in offer_analytics:
		offer_type = offer['offer_type']
		clicks = offer['clicks'] or 0
		conversions = offer['conversions'] or 0

		# Конверсия от кликов
		click_conversion = (conversions / clicks * 100) if clicks > 0 else 0

		# Конверсия от общего числа пользователей
		total_conversion = (conversions / total_users * 100) if total_users > 0 else 0

@router.message(Command("stats"), F.chat.type == "private", IsAdminFilter())
async def command_stats(message: Message, state: FSMContext, bot: Bot, user: User):
	await state.clear()

	users = await UserRepository.get_users()
	stats_events = await EventRepository.get_stats_events()
	stats_subscriptions = await SubscriptionRepository.get_stats_subscriptions()
	conversion_analytics = await AnalyticsRepository.get_conversion_analytics()

	count_users = len(users)
	conversions_data = {"count_users": count_users}

	for offer in conversion_analytics:
		clicks = offer['clicks'] or 0
		conversions = offer['conversions'] or 0

		conversion_clicks_from_users = (clicks / count_users * 100) if count_users > 0 else 0
		conversion_from_clicks = (conversions / clicks * 100) if clicks > 0 else 0
		conversion_from_users = (conversions / count_users * 100) if count_users > 0 else 0

		conversions_data.update({
			f"{offer['offer_type'].lower()}_conversion_clicks_from_users": f"{conversion_clicks_from_users:.1f}",
			f"{offer['offer_type'].lower()}_conversion_from_clicks": f"{conversion_from_clicks:.1f}",
			f"{offer['offer_type'].lower()}_conversion_from_users": f"{conversion_from_users:.1f}",
			f"{offer['offer_type'].lower()}_clicks": clicks,
			f"{offer['offer_type'].lower()}_conversions": conversions
		})


	file_path = save_to_excel(
		user_id=user.id,
		users=users,
		events=stats_events,
		subscriptions=stats_subscriptions
	)

	with open(file_path, 'rb') as file:
		input_file = BufferedInputFile(
			file=file.read(),
			filename="stats.xlsx"
		)

	text = i18n.translate(namespace="commands.stats", key="message", lang=user.language_code).format(
		**conversions_data
	)

	await message.answer_document(document=input_file, caption=text)
