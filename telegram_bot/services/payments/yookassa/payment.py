import urllib3
from yookassa import Configuration, Payment, Webhook
from yookassa.client import ApiClient

from configs import yookassa_config

class YookassaPayment:
	def __init__(self):
		Configuration.account_id = yookassa_config.SHOP_ID
		Configuration.secret_key = yookassa_config.API_KEY

		# Костыль с прокси
		proxy_url = "http://aCNdUU:KvuDeV@94.127.141.183:8000"

		proxy = urllib3.ProxyManager(proxy_url)

		# назначаем SDK свой HTTP-клиент
		Configuration.api_client = ApiClient(proxy)


	def _get_customer_data(self, email: str | None, phone: str | None) -> dict:
		"""Получение данных покупателя"""
		if email:
			return {"email": email}
		elif phone:
			return {"phone": str(phone)}
		else:
			return {"email": yookassa_config.DEFAULT_EMAIL}

	def create_payment(self,
		value: float,
		quantity: float,
		email: str | None = None,
		phone: str | None = None,
		metadata: dict | None = None
	):
		payment = Payment.create({
			"amount": {
				"value": f"{value:.2f}",
				"currency": "RUB"
			},
			"confirmation": {
				"type": "redirect",
				"return_url": "https://t.me/SXRaiBot"
			},
			"capture": True,
			"description": "Подписка на клуб",
			"receipt": {
				"customer": self._get_customer_data(email, phone),
				"items": [{
					"description": "Подписка на клуб",
					"quantity": f"{quantity:.2f}",
					"amount": {
						"value": f"{value:.2f}",
						"currency": "RUB"
					},
					"vat_code": "1",
					"payment_mode": "full_prepayment",
					"payment_subject": "service"
				}]
			},
			"metadata": metadata
		})
		return payment

	def get_payment(self, payment_id: str):
		return Payment.find_one(payment_id)

yookassa_payment = YookassaPayment()
