import asyncpg
from asyncpg import Connection, Pool, Record
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, List

from configs import database_config
from infrastructure.logger import get_logger

logger = get_logger("database")

@dataclass
class Transaction:
	"""Класс транзакции с удобным интерфейсом для запросов"""
	conn: Connection

	async def fetch(self, query: str, *args: Any) -> List[Record]:
		return await self.conn.fetch(query, *args)

	async def fetchrow(self, query: str, *args: Any) -> Record | None:
		return await self.conn.fetchrow(query, *args)

	async def fetchval(self, query: str, *args: Any, column: int = 0) -> Any:
		return await self.conn.fetchval(query, *args, column=column)

	async def execute(self, query: str, *args: Any) -> str:
		return await self.conn.execute(query, *args)

	async def executemany(self, query: str, values: List[tuple]) -> None:
		await self.conn.executemany(query, values)

class DatabaseManager:
	def __init__(self):
		self.pool: Pool | None = None

	async def connect(self) -> None:
		self.pool = await asyncpg.create_pool(
			dsn=str(database_config.DSN)
		)
		logger.info("🐘 Postgresql connected")

	async def close(self) -> None:
		if self.pool:
			await self.pool.close()
			logger.info("🐘 PostgreSQL disconnected")

	@asynccontextmanager
	async def transaction(self) -> AsyncIterator[Transaction]:
		"""Контекстный менеджер для транзакций с удобным интерфейсом"""
		if not self.pool:
			raise RuntimeError("Database pool is not initialized")

		async with self.pool.acquire() as conn:
			async with conn.transaction():
				yield Transaction(conn)

	async def fetch(self, query: str, *args: Any) -> List[Record]:
		"""Выполняет запрос и возвращает список записей."""
		async with self.pool.acquire() as conn:
			return await conn.fetch(query, *args)

	async def fetchrow(self, query: str, *args: Any) -> Record | None:
		"""Выполняет запрос и возвращает одну запись."""
		async with self.pool.acquire() as conn:
			return await conn.fetchrow(query, *args)

	async def fetchval(self, query: str, *args: Any, column: int = 0) -> Any:
		"""Выполняет запрос и возвращает значение."""
		async with self.pool.acquire() as conn:
			return await conn.fetchval(query, *args, column=column)

	async def execute(self, query: str, *args: Any) -> str:
		"""Выполняет запрос (INSERT/UPDATE/DELETE) и возвращает статус."""
		async with self.pool.acquire() as conn:
			return await conn.execute(query, *args)

	async def executemany(self, query: str, values: List[tuple]) -> None:
		"""Массовое выполнение запроса."""
		async with self.pool.acquire() as conn:
			await conn.executemany(query, values)

db = DatabaseManager()
