from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from keyboards import BaseCallbackData

class OfferCallbackData(BaseCallbackData, prefix="offer"):
	target: str | None = None

class OffersInlineKeyboard:
	@staticmethod
	def offers():
		builder = InlineKeyboardBuilder()
		builder.button(text="🎁 –30% на услуги студии", callback_data=OfferCallbackData(role="user", action="offer_studio"))
		builder.button(text="🎓 –50% на курс по нейрофото и нейровидео", callback_data=OfferCallbackData(role="user", action="offer_course"))
		builder.button(text="🧠 Клуб AI: 3 мес по цене 1", callback_data=OfferCallbackData(role="user", action="offer_club"))
		builder.button(text="📊 Полезные таблицы для работы на Озон", callback_data=OfferCallbackData(role="user", action="offer_ozon_tables"))
		builder.adjust(1)
		return builder.as_markup()

	def studio(channel_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="✅ Подписаться на канал", url=channel_url)
		builder.button(text="🔄 Я подписался(ась)", callback_data=OfferCallbackData(role="user", action="check_sub", target="studio"))
		builder.button(text="◀️ Назад", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def studio_success(studio_open_chat_link: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="💬 Оформить заказ со скидкой", url=studio_open_chat_link)
		builder.button(text="◀️ В меню", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def ozon_tables(channel_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="✅ Подписаться на канал", url=channel_url)
		builder.button(text="🔄 Я подписался(ась)", callback_data=OfferCallbackData(role="user", action="check_sub", target="ozon_tables"))
		builder.button(text="◀️ Назад", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def ozon_tables_success(ozon_tables_post_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="🔗 Перейти к посту с таблицами", url=ozon_tables_post_url)
		builder.button(text="◀️ В меню", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def course(course_telegraph_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="🎁 Получить промокод", callback_data=OfferCallbackData(role="user", action="course_promocodes"))
		builder.button(text="📘 Программа курса", url=course_telegraph_url)
		builder.button(text="◀️ Назад", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def course_success(course_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="🔗 Оплатить тариф", url=course_url)
		builder.button(text="◀️ В меню", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def club(club_info_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="💳 Оплатить со скидкой", callback_data=OfferCallbackData(role="user", action="pay_club"))
		# builder.button(text="ℹ️ Что внутри клуба", url=club_info_url)
		builder.button(text="◀️ Назад", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()

	def club_success(invite_link: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="🔓 Войти в SXR AI Club", url=invite_link)
		builder.adjust(1)
		return builder.as_markup()

	def payment(payment_url: str, show_btn_back: bool = True):
		builder = InlineKeyboardBuilder()
		builder.button(text="🔗 Перейти к оплате", url=payment_url)

		if show_btn_back:
			builder.button(text="◀️ В меню", callback_data=OfferCallbackData(role="user", action="main_menu"))

		builder.adjust(1)
		return builder.as_markup()

	def manager(manager_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="💬 Связаться с менеджером", url=manager_url)
		builder.button(text="◀️ В меню", callback_data=OfferCallbackData(role="user", action="main_menu"))
		builder.adjust(1)
		return builder.as_markup()
