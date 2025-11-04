from celery import Celery

from configs import redis_config
from infrastructure.logger import logger

app = Celery(
	"telegram_bot",
	broker=str(redis_config.DSN),
	backend=None,
	include=["celery_app.tasks.send_notification"]
)

app.conf.task_default_queue = "telegram_bot"
app.autodiscover_tasks(["celery_app.tasks"])

logger.info("Celery application configured with Redis at %s (prefork mode)", redis_config.DSN)
