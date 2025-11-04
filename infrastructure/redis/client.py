from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError, ConnectionError

from configs import redis_config
from infrastructure.logger import get_logger

logger = get_logger("redis")

pool = ConnectionPool.from_url(str(redis_config.DSN))
redis = Redis(connection_pool=pool)

async def check_redis():
	try:
		await redis.ping()
		logger.info("⚡️ Redis connected")
	except Exception as e:
		logger.info("Redis connection failed")
		raise e
