from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SCRAPE_", extra="ignore")

    # Rate limiting
    requests_per_second: float = 1.0
    max_retries: int = 3
    retry_backoff_multiplier: float = 1.0

    # Browser settings
    headless_browser: bool = True
    browser_timeout_ms: int = 30000

    # Logging
    log_level: str = "INFO"


class LastFMSettings(BaseSettings):
    """Last.fm API configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LASTFM_", extra="ignore")

    user: Optional[str] = None
    api_key: Optional[str] = None
    shared_secret: Optional[str] = None


class YouTubeSettings(BaseSettings):
    """YouTube API configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="YOUTUBE_", extra="ignore")

    api_key: Optional[str] = None


settings = Settings()
lastfm_settings = LastFMSettings()
youtube_settings = YouTubeSettings()
