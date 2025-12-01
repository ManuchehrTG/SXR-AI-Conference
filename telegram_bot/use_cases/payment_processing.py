from repositories.transaction import TransactionRepository
from services.payments.yookassa import yookassa_payment
from services.payment import PaymentService
from infrastructure.logger import logger

async def payment_processing():
	transactions = await TransactionRepository.get_pending_transactions()

	for transaction in transactions:
		try:
			payment = yookassa_payment.get_payment(payment_id=transaction.provider_tx_id)
			await PaymentService.process_payment(payment=payment)
		except Exception as e:
			logger.error(f"Ошибка при обработке транзакции с ID {transaction.id} ({transaction.provider_tx_id})", exc_info=True)
