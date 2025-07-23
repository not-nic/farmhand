"""
Module containing the config / settings for the Farmhand Application.
"""

from datetime import timedelta

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Farmhand"
    VERSION: str = "0.1"
    API_V1_STR: str = "/api/v1"

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ENVIRONMENT: str

    SERVICE_USER_USERNAME: str
    SERVICE_USER_EMAIL: str
    SERVICE_USER_PASSWORD: str

    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_OAUTH_CALLBACK_URL: str
    GITHUB_TOKEN_EXPIRATION_TIME: timedelta = timedelta(minutes=60)

    FRONTEND_REDIRECT_URL: str

    JWT_TOKEN_EXPIRATION_TIME: timedelta = timedelta(minutes=60)
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str

    DATA_API_URL: str = "http://localhost:8001/api/v1"

    @computed_field(return_type=str)
    def DATABASE_URL(self):
        if self.ENVIRONMENT == "development":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if self.ENVIRONMENT == "testing":
            return "sqlite:///./instance/testdb.sqlite"

        return None

    LOG_FORMAT: str = (
        "[%(asctime)s] - [%(levelname)s] - %(filename)s::%(funcName)s::%(lineno)s - %(message)s"
    )


settings = Settings()
