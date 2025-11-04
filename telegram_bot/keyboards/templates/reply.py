from aiogram.utils.keyboard import ReplyKeyboardBuilder

class TemplatesReplyKeyboard:
	@staticmethod
	def main_menu(access: str):
		builder = ReplyKeyboardBuilder()

		if access == "free":
			builder.button(text="💳 Оплатить")
			builder.button(text="📖 Частые вопросы")
		elif access == "paid":
			builder.button(text="❓ Вопросы по плану")
			builder.button(text="⚙️ Настройки")

		builder.adjust(1)
		return builder.as_markup(resize_keyboard=True)
