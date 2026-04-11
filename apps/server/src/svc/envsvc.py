"""
Application Environment Module
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path:
    """Climb up from current file to find .env"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".env").exists():
            return parent / ".env"
    # Fallback to local directory if not found
    return Path(".env")


class AppEnv(BaseSettings):
    """
    Application configuration loaded from .env file.
    """

    model_config = SettingsConfigDict(env_file=find_env_file(), extra="ignore")

    # App DB config
    app_db: str
    app_user: str
    app_password: str

    db_host: str = "localhost"
    db_port: int = 5432

    secret_key: str
    access_token_expire_seconds: int = 28800
    algorithm: str = "HS256"

    loglevel: int = 10

    @property
    def database_url(self) -> str:
        """
        Construct async SQLAlchemy database URL.
        """
        return (
            f"postgresql+asyncpg://"
            f"{self.app_user}:"
            f"{self.app_password}@"
            f"{self.db_host}:"
            f"{self.db_port}/"
            f"{self.app_db}"
        )
