import logging
from configs import logger_config

from .config import LOGGING_CONFIG
from .utils import get_logger, log_execution_time, LoggerMixin

# import os
# print(f"Logger initialized in PID={os.getpid()}")

class LoggerSetup:
	def __init__(self):
		self.config = logger_config
		self._initialized = False

	def setup_logging(self) -> None:
		"""Инициализация системы логирования"""
		if self._initialized:
			return

		# Создаем директорию для логов
		if self.config.ENABLE_FILE_LOGGING:
			self.config.DIR.mkdir(exist_ok=True)

		# Обновляем конфигурацию на основе настроек
		self._update_logging_config()

		# Применяем конфигурацию
		logging.config.dictConfig(LOGGING_CONFIG)
		self._initialized = True

		# Логируем успешную инициализацию
		logger = logging.getLogger("infrastructure.logger")
		logger.info("🚀 Logger initialized successfully")

	def _update_logging_config(self) -> None:
		# Обновляем уровни логирования
		for logger_config in LOGGING_CONFIG["loggers"].values():
			logger_config["level"] = self.config.LEVEL

		# Настраиваем обработчики
		handlers = []

		if self.config.ENABLE_CONSOLE_LOGGING:
			handlers.append("console")
			LOGGING_CONFIG["handlers"]["console"]["level"] = self.config.LEVEL

		if self.config.ENABLE_FILE_LOGGING:
			log_file = self.config.DIR / "app.log"
			LOGGING_CONFIG["handlers"]["file"]["filename"] = str(log_file)
			LOGGING_CONFIG["handlers"]["file"]["maxBytes"] = self.config.MAX_LOG_SIZE * 1024 * 1024
			LOGGING_CONFIG["handlers"]["file"]["backupCount"] = self.config.BACKUP_COUNT
			LOGGING_CONFIG["handlers"]["file"]["level"] = self.config.LEVEL
			handlers.append("file")

		# Обновляем обработчики для всех логгеров
		for logger_config in LOGGING_CONFIG["loggers"].values():
			logger_config["handlers"] = handlers

# Глобальная инициализация
logger_setup = LoggerSetup()
logger_setup.setup_logging()

# Экспорт основного логгера
logger = logging.getLogger("app")

__all__ = ['logger', 'logger_setup', 'logger_config', 'get_logger', 'log_execution_time', 'LoggerMixin']
