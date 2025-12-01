import json
from yookassa import Payment

from repositories.transaction import TransactionRepository
from schemes.user import User
from schemes.transaction import TransactionOfferType, TransactionType, TransactionStatusType
from services.offer import OfferService
from services.payments.yookassa import yookassa_payment
from infrastructure.logger import logger

class PaymentService:
	@staticmethod
	async def create_payment(user: User, offer: TransactionOfferType, type: TransactionType, value: float, quantity: float, metadata: dict | None = None) -> str:
		transaction = await TransactionRepository.get_by_user_id_and_offer_and_status(user_id=user.id, offer=offer, status="pending")
		if transaction:
			payment = yookassa_payment.get_payment(payment_id=transaction.provider_tx_id)
			if payment.status == "pending":
				return transaction.provider_payload_obj.confirmation.confirmation_url
			else:
				await TransactionRepository.update_status(tx_id=transaction.id, status=payment.status)

		payment = yookassa_payment.create_payment(
			value=value,
			quantity=quantity,
			email=user.email,
			metadata=metadata
		)

		await TransactionRepository.create_transaction(
			user_id=user.id,
			offer=offer,
			type=type,
			amount=value,
			quantity=quantity,
			provider_tx_id=payment.id,
			provider_payload=json.dumps(dict(payment), default=str),
			status=TransactionStatusType.PENDING
		)

		return payment.confirmation.confirmation_url

	@staticmethod
	async def process_webhook(data: dict):
		payment_id = data["object"]["id"]
		try:
			payment = yookassa_payment.get_payment(payment_id=payment_id)
			await PaymentService.process_payment(payment=payment)
		except Exception as e:
			logger.error(f"[WEBHOOK] Ошибка при обработке платежа с ID {payment_id}", exc_info=True)

	@staticmethod
	async def process_payment(payment: Payment):
		transaction = await TransactionRepository.get_by_provider_tx_id(provider_tx_id=payment.id)
		if not transaction:
			return

		if transaction.status == TransactionStatusType.PENDING and payment.status == "succeeded":
			await TransactionRepository.update_status(tx_id=transaction.id, status="succeeded")
			await OfferService.handle_successful_payment(transaction=transaction)
		elif transaction.status == TransactionStatusType.PENDING and payment.status == "canceled":
			await TransactionRepository.update_status(tx_id=transaction.id, status="canceled")
