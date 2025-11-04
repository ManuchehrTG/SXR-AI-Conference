from datetime import datetime
from typing import List
from uuid import UUID

from infrastructure.database import db
from schemes.transaction import TransactionOfferType, TransactionStatusType
from schemes.subscription import Subscription, SubscriptionStats

class SubscriptionRepository:
	@staticmethod
	async def create_subscription(
		user_id: int,
		offer: TransactionOfferType,
		started_at: datetime,
		expires_at: datetime
	):
		record = await db.fetchrow(
			"""
			INSERT INTO subscriptions (user_id, offer, started_at, expires_at, updated_at)
			VALUES ($1, $2, $3, $4, $5)
			RETURNING *
			""",
			user_id,
			offer,
			started_at,
			expires_at,
			started_at
		)
		return Subscription(**record)

	@staticmethod
	async def update_subscription(subscription_id: int, add_days: int):
		record = await db.fetchrow(
			"""
			UPDATE subscriptions SET
				expires_at = expires_at + make_interval(days => $1),
				status = 'active',
				updated_at = now()
			WHERE id = $2
			RETURNING *
			""",
			add_days, subscription_id
		)
		return Subscription(**record)

	@staticmethod
	async def update_subscription_status(subscription_id: int, status: TransactionStatusType):
		await db.execute("UPDATE subscriptions SET status = $1 WHERE id = $2", status, subscription_id)

	@staticmethod
	async def create_subscription_transaction(subscription_id: str, transaction_id: UUID, type: str):
		await db.execute("INSERT INTO subscription_transactions (sub_id, tx_id, type) VALUES ($1, $2, $3)", subscription_id, transaction_id, type)

	@staticmethod
	async def get_by_user_id_and_offer_and_status(user_id: int, offer: TransactionOfferType, status: TransactionStatusType):
		record = await db.fetchrow("SELECT * FROM subscriptions WHERE user_id = $1 AND offer = $2 AND status = $3", user_id, offer, status)
		if record:
			return Subscription(**record)

	@staticmethod
	async def get_expiring_subscriptions(expires_at: datetime):
		records = await db.fetch(
			"""
			SELECT *
			FROM subscriptions
			WHERE expires_at = $1 AND status = 'active'
			""",
			expires_at
		)
		return [Subscription(**record) for record in records]

	@staticmethod
	async def get_expired_subscriptions():
		records = await db.fetch(
			"""
			SELECT *
			FROM subscriptions
			WHERE expires_at <= now() AND status = 'active'
			"""
		)
		return [Subscription(**record) for record in records]

	@staticmethod
	async def get_stats_subscriptions():
		records = await db.fetch(
			"""
			SELECT
				s.*,
				u.username AS username
			FROM subscriptions s
			LEFT JOIN users u ON u.id = s.user_id
			"""
		)
		return [SubscriptionStats(**record) for record in records]
