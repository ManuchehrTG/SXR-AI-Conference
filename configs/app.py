from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List

class AppConfig(BaseSettings):
	PROJECT_NAME: str
	LANGUAGES: List[str] = Field(default_factory=list)
	DEFAULT_LANGUAGE: str
	TIME_ZONE: str

	STORAGE_DIR: str
	DOWNLOAD_DIR: str

	DEBUG: bool
	HOST: str

app_config = AppConfig()
