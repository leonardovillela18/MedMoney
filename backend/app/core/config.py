from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = 'sqlite:///./medmoney.db'
    jwt_secret_key: str = 'development-only-change-me'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    frontend_origins: str = 'http://localhost:5173'
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    @property
    def origins(self) -> list[str]: return [item.strip() for item in self.frontend_origins.split(',')]

@lru_cache
def get_settings() -> Settings: return Settings()
