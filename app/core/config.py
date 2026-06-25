from functools import lru_cache
import json
from typing import Literal

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="AI Scheduler Engine", alias="APP_NAME")
    app_env: Literal["local", "development", "testing", "staging", "production"] = Field(
        default="local",
        alias="APP_ENV",
    )
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_api_prefix: str = Field(default="/api/v1", alias="APP_API_PREFIX")
    backend_cors_origins: str = Field(default="", alias="BACKEND_CORS_ORIGINS")

    database_url: str = Field(
        default="postgresql+psycopg://scheduler:scheduler@localhost:5432/ai_scheduler",
        alias="DATABASE_URL",
    )

    jwt_secret: str = Field(default="change-me-in-local-env", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    ai_provider: str = Field(default="joinbareng", alias="AI_PROVIDER")
    ai_base_url: str = Field(default="", alias="AI_BASE_URL")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_model: str = Field(default="", alias="AI_MODEL")

    @field_validator("app_api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        value = (value or "/api/v1").strip()
        if not value.startswith("/"):
            value = f"/{value}"
        return value.rstrip("/") or "/api/v1"

    @field_validator("database_url", mode="before")
    @classmethod
    def default_database_url_when_blank(cls, value: str | None) -> str:
        if value is None or str(value).strip() == "":
            return "postgresql+psycopg://scheduler:scheduler@localhost:5432/ai_scheduler"
        return str(value)

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        raw_value = self.backend_cors_origins.strip()
        if not raw_value:
            return []

        if raw_value.startswith("["):
            parsed = json.loads(raw_value)
            if not isinstance(parsed, list):
                raise ValueError("BACKEND_CORS_ORIGINS JSON value must be a list")
            return [str(origin).strip() for origin in parsed if str(origin).strip()]

        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
