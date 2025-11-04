import asyncio
import asyncpg
import os
from pathlib import Path

from infrastructure.database import db
from infrastructure.logger import get_logger

logger = get_logger("database")

async def main():
	# db_url = os.getenv("DATABASE_URL")
	# conn = await asyncpg.connect(db_url)

	await db.connect()

	sql_path = Path(__file__).parent / "migrations/001_scheme.sql"
	if sql_path.exists():
		query = sql_path.read_text()
		await db.execute(query)

	# await conn.close()
	await db.close()

	logger.info("- Database initialized ✅")

if __name__ == "__main__":
	asyncio.run(main())
