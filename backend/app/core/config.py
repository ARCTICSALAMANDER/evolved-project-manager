from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    DB_PASSWORD: str
    DB_USER: str
    HOST: str
    DB_PORT: int
    JWT_KEY: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")),
        env_file_encoding="utf-8"
    )