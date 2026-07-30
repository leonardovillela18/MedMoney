from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    environment: str = 'development'
    app_version: str = '0.2.0'
    database_url: str = 'sqlite:///./crmoney.db'
    jwt_secret_key: str = 'development-only-change-me'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    session_idle_timeout_minutes: int = 15
    password_reset_token_expire_minutes: int = 30
    email_provider: str = 'console'
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_from_name: str = 'CRMoney'
    smtp_use_tls: bool = True
    frontend_url: str = 'http://localhost:5173'
    frontend_origins: str = 'http://localhost:5173'
    redis_url: str | None = None
    storage_backend: str = 'local'
    storage_path: str = 'uploads'
    log_level: str = 'INFO'
    trusted_hosts: str = 'localhost,127.0.0.1,testserver'
    enable_docs: bool = True
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    @property
    def origins(self) -> list[str]: return [item.strip() for item in self.frontend_origins.split(',')]
    @property
    def hosts(self) -> list[str]: return [item.strip() for item in self.trusted_hosts.split(',')]
    @model_validator(mode='after')
    def secure_production(self):
        if self.environment == 'production' and (self.jwt_secret_key == 'development-only-change-me' or len(self.jwt_secret_key)<32): raise ValueError('JWT_SECRET_KEY must be a strong secret in production')
        if self.environment == 'production' and self.enable_docs: raise ValueError('ENABLE_DOCS must be false in production')
        if self.environment == 'production' and self.email_provider != 'smtp': raise ValueError('EMAIL_PROVIDER must be smtp in production')
        if self.environment == 'production' and not all((self.smtp_host,self.smtp_user,self.smtp_password,self.smtp_from)): raise ValueError('SMTP configuration is required in production')
        return self

@lru_cache
def get_settings() -> Settings: return Settings()
