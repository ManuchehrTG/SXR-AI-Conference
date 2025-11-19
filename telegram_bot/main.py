import asyncio
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import yookassa
from core.container import container
from configs import app_config, telegram_bot_config
from infrastructure.database import db
from infrastructure.logger import logger, get_logger
from infrastructure.redis import redis, check_redis
from infrastructure.scheduler import APSchedulerAdapter
from infrastructure.scheduler.models import JobType, JobConfig
from middlewares import register_middlewares
from use_cases.notification import payment_notification, kick_user_notification, check_spamming
from use_cases.payment_processing import payment_processing

async def create_app() -> FastAPI:
	await db.connect()
	await check_redis()

	storage = RedisStorage(redis)
	dp = Dispatcher(storage=storage)
	bot = Bot(token=telegram_bot_config.TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

	container.bot = bot

	register_middlewares(dp=dp)

	from handlers import router

	dp.include_router(router)

	logger.info("🟢 The bot is running!")

	# Только при старте бота
	await payment_processing()

	scheduler_logger = get_logger("apscheduler")

	scheduler = APSchedulerAdapter()
	payment_notification_job = JobConfig(
		job_id="payment_notification",
		func=payment_notification,
		trigger_type=JobType.CRON,
		cron_expr="0 12 * * *",
		timezone=app_config.TIME_ZONE
	)
	kick_user_notification_job = JobConfig(
		job_id="kick_user_notification",
		func=kick_user_notification,
		trigger_type=JobType.CRON,
		cron_expr="01 20 * * *",
		timezone=app_config.TIME_ZONE,
		args=[bot]
	)
	check_spamming_job = JobConfig(
		job_id="check_spamming",
		func=check_spamming,
		trigger_type=JobType.INTERVAL,
		minutes=1,
		timezone=app_config.TIME_ZONE,
		args=[bot]
	)
	await scheduler.add_job(payment_notification_job)
	await scheduler.add_job(kick_user_notification_job)
	await scheduler.add_job(check_spamming_job)
	await scheduler.start()

	scheduler_logger.setLevel(30)

	@asynccontextmanager
	async def lifespan(app: FastAPI):
		try:
			await bot.set_webhook(url=f"{telegram_bot_config.DOMAIN}/webhook") # Добавить 'https://' если не запустится
			yield  # Здесь работает приложение
		except Exception as e:
			logger.error(f"⚠️ Startup failed: {e}", exc_info=True)
			raise
		finally:
			logger.info("🔴 Shutting down...")
			try:
				await bot.delete_webhook()
				await bot.session.close()
				await dp.storage.close()
				await redis.aclose()
				await db.close()
				logger.info("🤖 Aiogram bot session closed")
			except Exception as e:
				logger.error(f"Error during shutdown: {e}", exc_info=True)

	# Создание экземпляра FastAPI
	app = FastAPI(
		title=app_config.PROJECT_NAME,
		version="1.0.0",
		lifespan=lifespan,
		docs_url="/api/docs" if app_config.DEBUG else None
	)

	# Настройка CORS
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"]
	)

	@app.post("/webhook")
	async def bot_webook(update: dict):
		"""Обработка обновлений через вебхук."""
		try:
			telegram_update = Update(**update)
			await dp.feed_update(bot=bot, update=telegram_update)
		except Exception as e:
			logger.exception(f"Error processing update: {e}")
		finally:
			return {"status": "ok"}

	@app.get("/health")
	async def health_check():
		return {"message": "ok", "status": "healthy"}

	app.include_router(yookassa.router)

	return app

async def main() -> None:
	app = await create_app()

	config = uvicorn.Config(app=app, host=app_config.HOST, port=telegram_bot_config.PORT, log_level="info", access_log=False)
	server = uvicorn.Server(config)

	await server.serve()

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logger.info("🔴 Server stopped gracefully")