from redis import Redis
from redis.connection import ConnectionPool

from configs import redis_config
from infrastructure.logger import get_logger

logger = get_logger("sync_redis")

sync_pool = ConnectionPool.from_url(str(redis_config.DSN))
sync_redis = Redis(connection_pool=sync_pool)

def check_sync_redis():
	try:
		sync_redis.ping()
		logger.info("🔌 Sync Redis connected")
	except Exception as e:
		logger.error(f"Sync Redis connection failed: {e}")
		raise e