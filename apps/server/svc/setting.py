from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    # Postgres bootstrap
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # App DB config
    app_db: str
    app_user: str
    app_password: str

    # optional extras
    db_host: str = "localhost"
    db_port: int = 5432