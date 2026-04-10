"""
Application Environment Module
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class AppEnv(BaseSettings):
    """
    Application configuration loaded from .env file.
    """
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore"
    )

    # App DB config
    app_db: str
    app_user: str
    app_password: str

    db_host: str = "localhost"
    db_port: int = 5432
