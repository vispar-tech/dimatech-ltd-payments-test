from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


class LogLevel(StrEnum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Tags(StrEnum):
    """Tags for API routes."""


class Settings(BaseSettings):
    """Application settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    allowed_hosts: str = "*"
    workers_count: int = 1
    reload: bool = False

    jwt_cookie_domain: str | None = None
    # Use Field to to avoid Ruff S105(hardcoded password)
    jwt_users_secret: str = Field(default="users_secret")

    payments_secret_key: str = Field(default="payments_secret")

    log_level: LogLevel = LogLevel.INFO
    log_file_enabled: bool = False

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "admin"
    # Use Field to to avoid Ruff S105(hardcoded password)
    db_pass: str = Field(default="admin")
    db_base: str = "payments_db"
    db_echo: bool = False

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PAYMENTS_APP_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
