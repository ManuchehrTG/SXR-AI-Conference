import httpx
from celery.exceptions import Retry, MaxRetriesExceededError

from celery_app import app
from configs import telegram_bot_config
from infrastructure.http import sync_http_client
from infrastructure.redis import sync_redis as redis
from infrastructure.logger import logger

@app.task(bind=True, rate_limit="30/s", max_retries=3, ignore_result=True)
def send_telegram(self, spamming_id: str, user_id: int, content_type: str, **kwargs):
	url_templates = {
		"text": "sendMessage",
		"photo": "sendPhoto", 
		"video": "sendVideo",
		"media_group": "sendMediaGroup"
	}

	if content_type not in url_templates:
		redis.hincrby(f"spamming_id:{spamming_id}", "failed", 1)
		raise ValueError(f"Unsupported content_type: {content_type}")

	url = f"https://api.telegram.org/bot{telegram_bot_config.TOKEN}/{url_templates[content_type]}"
	payload = {
		"chat_id": user_id,
		**kwargs
	}

	try:
		sync_http_client.post(url=url, response_type="response", raise_for_status=True, data=payload)
		redis.hincrby(f"spamming_id:{spamming_id}", "processed", 1)
		redis.hincrby(f"spamming_id:{spamming_id}", "successful", 1)
	except httpx.HTTPStatusError as e:
		status_code = e.response.status_code

		if status_code == 429:
			retry_after = int(e.response.headers.get("Retry-After", 60))
			logger.warning(f"Telegram rate limit hit. Retry after {retry_after}s")
			raise self.retry(countdown=retry_after, exc=e)

		elif status_code >= 400:
			error_text = e.response.text.lower()

			soft_errors = [
				"bot was blocked by the user",
				"user is deactivated", 
				"chat not found",
				"user_is_blocked",
			]

			if any(phrase in error_text for phrase in soft_errors):
				logger.info(f"Soft error for user {user_id}: {error_text}")
				redis.hincrby(f"spamming_id:{spamming_id}", "processed", 1)
				redis.hincrby(f"spamming_id:{spamming_id}", "failed", 1)
				return

			if 400 <= status_code < 500:
				logger.error(f"Telegram client error {status_code}: {e.response.text}")
				redis.hincrby(f"spamming_id:{spamming_id}", "processed", 1)
				redis.hincrby(f"spamming_id:{spamming_id}", "failed", 1)
				return

			if status_code >= 500:
				logger.error(f"Telegram server error {status_code}: {e.response.text}")
				raise self.retry(countdown=min(60 * (2 ** self.request.retries), 86400), exc=e)

	except (httpx.RequestError, httpx.TimeoutException) as e:
		logger.error(f"Network/timeout error: {str(e)}")
		raise self.retry(countdown=10 * (self.request.retries + 1), exc=e)

	except MaxRetriesExceededError as e:
		logger.warning(f"Max retries exceeded for user_id={user_id}")
		redis.hincrby(f"spamming_id:{spamming_id}", "processed", 1)
		redis.hincrby(f"spamming_id:{spamming_id}", "failed", 1)

	except Retry:
		raise

	except Exception as e:
		# logger.error(f"Telegram send error: {str(e)}")
		logger.exception(f"Unexpected Telegram send error: {e}")
		delay = min(60 * (2 ** self.request.retries), 86400)
		raise self.retry(countdown=delay, exc=e)
