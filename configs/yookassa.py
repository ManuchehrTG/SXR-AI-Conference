from pydantic_settings import BaseSettings

class YooKassaConfig(BaseSettings):
	API_KEY: str
	SHOP_ID: str
	DEFAULT_EMAIL: str

	class Config:
		env_prefix = "YOOKASSA_"

yookassa_config = YooKassaConfig()
