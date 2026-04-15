"""SnapStash configuration — all settings with env variable overrides."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings. Override any value via environment variables."""

    # --- Storage ---
    storage_path: str = os.getenv("STORAGE_PATH", "/data/snapstash/photos")
    temp_path: str = os.getenv("TEMP_PATH", "/data/snapstash/temp")
    db_path: str = os.getenv("DB_PATH", "/data/snapstash/metadata.db")

    # --- Upload ---
    chunk_size: int = 5 * 1024 * 1024  # 5 MB
    max_upload_size: int = 10 * 1024 * 1024 * 1024  # 10 GB

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]

    # --- App ---
    app_name: str = "SnapStash"
    app_version: str = "1.0.0"
    base_url: str = os.getenv("BASE_URL", "http://snapstash.local")

    class Config:
        env_prefix = "SNAPSTASH_"


settings = Settings()


def ensure_directories():
    """Create required directories if they don't exist."""
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)
    Path(settings.temp_path).mkdir(parents=True, exist_ok=True)
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
