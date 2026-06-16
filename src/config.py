"""
Module containing the config / settings for the Farmhand Application.
"""

import os
from datetime import timedelta

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettingsConfig(BaseSettings):
    """Shared settings"""

    PROJECT_NAME: str = "Farmhand"
    VERSION: str = "0.1"
    API_V1_STR: str = "/api/v1"

    JWT_TOKEN_EXPIRATION_TIME: timedelta = timedelta(minutes=60)
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str

    GITHUB_TOKEN_EXPIRATION_TIME: timedelta = timedelta(minutes=60)

    DATA_API_URL: str = "http://localhost:8001/api/v1"
    FRONTEND_REDIRECT_URL: str

    LOG_FORMAT: str = (
        "[%(asctime)s] - [%(levelname)s] - %(filename)s::%(funcName)s::%(lineno)s - %(message)s"
    )


class Settings(BaseSettingsConfig):
    """Default settings for the application."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SERVICE_USER_USERNAME: str
    SERVICE_USER_EMAIL: str
    SERVICE_USER_PASSWORD: str

    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_OAUTH_CALLBACK_URL: str

    @computed_field(return_type=str)
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class TestSettings(BaseSettingsConfig):
    """Settings for unit tests"""

    SERVICE_USER_USERNAME: str = "unit-tester"
    SERVICE_USER_EMAIL: str = "unit-test@farmhand.uk"
    SERVICE_USER_PASSWORD: str = "password"

    GITHUB_CLIENT_ID: str = "unit-testing"
    GITHUB_CLIENT_SECRET: str = "unit-testing"
    GITHUB_OAUTH_CALLBACK_URL: str = "unit-testing"

    JWT_SECRET_KEY: str = "unit-testing"
    FRONTEND_REDIRECT_URL: str = "/docs"

    DATABASE_URL: str = "sqlite:///./instance/testdb.sqlite"


def get_settings() -> BaseSettingsConfig:
    """
    Function to get the correct configuration based on the
    testing .env variable.
    :return: Setting or TestSettings configuration.
    """
    testing = os.getenv("TESTING", "").lower() == "true"
    return TestSettings() if testing else Settings()


settings = get_settings()
