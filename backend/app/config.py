from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret: str = Field(alias="JWT_SECRET")
    access_token_minutes: int = Field(default=60, alias="ACCESS_TOKEN_MINUTES")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    app_environment: str = Field(default="development", alias="APP_ENVIRONMENT")

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
