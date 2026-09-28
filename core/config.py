"""
Core configuration module.

Loads settings from environment variables using pydantic-settings.
All application-wide configuration is centralized here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "TAPI"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ── PostgreSQL ──────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tapi_db"
    POSTGRES_USER: str = "tapi_user"
    POSTGRES_PASSWORD: str = "tapi_pass"

    @property
    def POSTGRES_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def POSTGRES_URL_SYNC(self) -> str:
        """Synchronous URL for Alembic migrations."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── MongoDB ─────────────────────────────────────────
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "tapi_db"
    MONGO_USER: str = "tapi_user"
    MONGO_PASSWORD: str = "tapi_pass"

    @property
    def MONGO_URL(self) -> str:
        return (
            f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
            f"@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
            f"?authSource=admin"
        )

    # ── Redis ───────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ── Google OAuth2 ───────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # ── Google Maps ─────────────────────────────────────
    GOOGLE_MAPS_API_KEY: str = ""

    # ── SendGrid ────────────────────────────────────────
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@tapi.app"

    # ── JWT ─────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Celery ──────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"


settings = Settings()
