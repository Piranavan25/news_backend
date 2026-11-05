from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Tamil News Scraper"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    SUPABASE_URL: str
    SUPABASE_SECRET_KEY: str

    HTTP_TIMEOUT: int = 30
    HTTP_MAX_CONNECTIONS: int = 20
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 10
    MAX_CONCURRENT_ARTICLES: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()