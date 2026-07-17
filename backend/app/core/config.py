from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    environment: str = 'development'
    app_version: str = '0.2.0'
    database_url: str = 'sqlite:///./medmoney.db'
    jwt_secret_key: str = 'development-only-change-me'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
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
        return self

@lru_cache
def get_settings() -> Settings: return Settings()
