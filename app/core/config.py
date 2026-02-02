from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):

    ENVIRONMENT: Literal["dev", "prod", "test"] = "dev"
    DEBUG: bool = False

    DATABASE_URL: str
    REDIS: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    SWAPI_BASE: str
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

settings = Settings()