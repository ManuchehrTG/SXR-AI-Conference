from pathlib import Path
from pydantic_settings import BaseSettings

class LoggerConfig(BaseSettings):
	# Уровни логирования
	LEVEL: str
	FORMAT: str

	# Файлы логов
	DIR: Path
	ENABLE_FILE_LOGGING: bool
	ENABLE_CONSOLE_LOGGING: bool

	# Ротация логов
	MAX_LOG_SIZE: int
	BACKUP_COUNT: int

	class Config:
		env_prefix = "LOGGER_"

logger_config = LoggerConfig()
