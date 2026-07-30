from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    app_version: str = "0.2.0"
    database_url: str = "sqlite:///./crmoney.db"

    jwt_secret_key: str = "development-only-change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    session_idle_timeout_minutes: int = 15

    password_reset_token_expire_minutes: int = 30

    # Email
    email_provider: str = "console"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_from_name: str = "CRMoney"

    # STARTTLS, normalmente usado na porta 587
    smtp_use_tls: bool = True

    # SSL implícito, normalmente usado na porta 465
    smtp_use_ssl: bool = False

    frontend_url: str = "http://localhost:5173"
    frontend_origins: str = "http://localhost:5173"

    redis_url: str | None = None

    storage_backend: str = "local"
    storage_path: str = "uploads"

    log_level: str = "INFO"

    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    enable_docs: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def origins(self) -> list[str]:
        return [
            item.strip()
            for item in self.frontend_origins.split(",")
            if item.strip()
        ]

    @property
    def hosts(self) -> list[str]:
        return [
            item.strip()
            for item in self.trusted_hosts.split(",")
            if item.strip()
        ]

    @model_validator(mode="after")
    def validate_settings(self):
        if (
            self.environment == "production"
            and (
                self.jwt_secret_key == "development-only-change-me"
                or len(self.jwt_secret_key) < 32
            )
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be a strong secret in production"
            )

        if self.environment == "production" and self.enable_docs:
            raise ValueError(
                "ENABLE_DOCS must be false in production"
            )

        # SSL implícito e STARTTLS são modos diferentes.
        # Não devem ficar ativados ao mesmo tempo.
        if self.smtp_use_ssl and self.smtp_use_tls:
            raise ValueError(
                "SMTP_USE_SSL and SMTP_USE_TLS cannot both be true"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()