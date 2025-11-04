from datetime import datetime
from typing import List
from uuid import UUID

from infrastructure.database import db
from schemes.transaction import Transaction, TransactionOfferType, TransactionType, TransactionStatusType

class TransactionRepository:
	@staticmethod
	async def create_transaction(
		user_id: int,
		offer: TransactionOfferType,
		type: TransactionType,
		amount: float,
		quantity: float,
		provider_tx_id: str,
		provider_payload: dict,
		status: TransactionStatusType
	):
		record = await db.fetchrow(
			"""
			INSERT INTO transactions (user_id, offer, type, amount, quantity, provider_tx_id, provider_payload, status)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
			RETURNING *
			""",
			user_id,
			offer,
			type,
			amount,
			quantity,
			provider_tx_id,
			provider_payload,
			status
		)
		return Transaction(**record)

	@staticmethod
	async def get_by_provider_tx_id(provider_tx_id: str):
		record = await db.fetchrow("SELECT * FROM transactions WHERE provider_tx_id = $1", provider_tx_id)
		if record:
			return Transaction(**record)

	@staticmethod
	async def get_by_user_id_and_offer_and_status(user_id: int, offer: TransactionOfferType, status: TransactionStatusType):
		record = await db.fetchrow("SELECT * FROM transactions WHERE user_id = $1 AND offer = $2 AND status = $3", user_id, offer, status)
		if record:
			return Transaction(**record)

	@staticmethod
	async def update_status(tx_id: UUID, status: TransactionStatusType):
		await db.execute("UPDATE transactions SET status = $1 WHERE id = $2", status, tx_id)
