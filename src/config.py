import os


class Config:
    PROJECT_NAME: str = "Farmhand"
    VERSION: str = "0.1"

    POSTGRES_HOST: str = os.getenv("DB_HOST")
    POSTGRES_PORT: int = os.getenv("DB_PORT", 5432)
    POSTGRES_USER: str = os.getenv("DB_USER")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD")
    POSTGRES_DB: str = os.getenv("DB_NAME")
    ENVIRONMENT: str = os.getenv("ENV", "testing")

    if ENVIRONMENT == "development":
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    if ENVIRONMENT == "testing":
        DATABASE_URL = "sqlite:///./testdb.sqlite"

config = Config()