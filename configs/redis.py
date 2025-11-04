from pydantic import computed_field
from pydantic_settings import BaseSettings

class RedisConfig(BaseSettings):
	HOST: str
	PORT: int
	DB: int
	USERNAME: str | None = None
	PASSWORD: str | None = None

	@computed_field
	@property
	def DSN(self) -> str:
		if self.USERNAME and self.PASSWORD:
			# Redis 6+ с ACL
			return f"redis://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
		elif self.PASSWORD:
			# Только пароль
			return f"redis://:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
		else:
			# Без аутентификации
			return f"redis://{self.HOST}:{self.PORT}/{self.DB}"

	class Config:
		env_prefix = "REDIS_"

redis_config = RedisConfig()
