from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SCRAPE_")

    # Rate limiting
    requests_per_second: float = 1.0
    max_retries: int = 3
    retry_backoff_multiplier: float = 1.0

    # Browser settings
    headless_browser: bool = True
    browser_timeout_ms: int = 30000

    # Logging
    log_level: str = "INFO"


settings = Settings()
