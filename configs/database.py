from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings
from pydantic_core import MultiHostUrl

class DatabaseConfig(BaseSettings):
	NAME: str
	USER: str
	PASSWORD: str
	HOST: str
	PORT: int

	@computed_field
	@property
	def DSN(self) -> PostgresDsn:
		return MultiHostUrl.build(
			scheme="postgresql",
			username=self.USER,
			password=self.PASSWORD,
			host=self.HOST,
			port=self.PORT,
			path=self.NAME,
		)

	class Config:
		env_prefix = "DATABASE_"

database_config = DatabaseConfig()
