import httpx
from celery.exceptions import Retry, MaxRetriesExceededError

from celery_app import app
from configs import telegram_bot_config
from infrastructure.http import sync_http_client
from infrastructure.logger import logger

@app.task(bind=True, rate_limit="30/s", max_retries=3, ignore_result=True)
def send_notification(self, user_id: int, text: str, reply_markup: dict | None = None):
	url = f"https://api.telegram.org/bot{telegram_bot_config.TOKEN}"
	method = "sendMessage"

	params = {
		"chat_id": user_id,
		"text": text,
		"parse_mode": "HTML"
	}
	if reply_markup:
		params["reply_markup"] = reply_markup

	try:
		sync_http_client.post(url=f"{url}/{method}", response_type="response", raise_for_status=True, data=params)
	except httpx.HTTPStatusError as e:
		status_code = e.response.status_code

		if status_code == 429:
			retry_after = e.response.headers.get("Retry-After", 60)
			retry_after = int(retry_after)
			logger.warning(f"Telegram rate limit hit. Retry after {retry_after}s")
			raise self.retry(countdown=retry_after, exc=e)

		elif status_code >= 400:
			error_text = e.response.text.lower()
			if any(phrase in error_text for phrase in [
				"bot was blocked by the user",
				"user is deactivated",
				"chat not found",
				"user_is_blocked",
			]):
				return

		logger.error(f"Telegram API error {status_code}: {e.response.text}")
		# raise self.retry(countdown=30, exc=e)

	except httpx.RequestError as e:
		logger.error(f"Network error: {str(e)}")
		raise self.retry(countdown=10 * (self.request.retries + 1), exc=e)

	except MaxRetriesExceededError as e:
		logger.warning(f"Max retries exceeded for user_id={user_id}")

	except Retry:
		raise

	except Exception as e:
		# logger.error(f"Telegram send error: {str(e)}")
		logger.exception(f"Unexpected Telegram send error: {e}")
		delay = min(60 * (2 ** self.request.retries), 86400)
		raise self.retry(countdown=delay, exc=e)
