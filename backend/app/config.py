from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MXBCASH_")

    db_path: str = str(Path(__file__).parent.parent / "mxbcash.db")
    debug: bool = False
    default_reporting_currency: str = "USD"


settings = Settings()
