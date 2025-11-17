from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import BaseCallbackData

class TemplatesInlineKeyboard:
	@staticmethod
	def privacy(privacy_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="Политика и конфиденциальность", url=privacy_url)
		builder.button(text="Согласен(а)", callback_data=BaseCallbackData(role="user", action="accept_privacy"))
		builder.adjust(1)
		return builder.as_markup()

	@staticmethod
	def admin_menu():
		builder = InlineKeyboardBuilder()
		builder.button(text="Рассылка", callback_data=BaseCallbackData(role="admin", action="spamming"))
		builder.adjust(1)
		return builder.as_markup()
