"""
Entrypoint for starting the application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.core.db import create_db_and_tables
from src.api.routes import api_router
from src.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield  # Continue running the app

app = FastAPI(
    title=f"{config.PROJECT_NAME}-{config.VERSION}",
    lifespan=lifespan
)
app.include_router(api_router, prefix="/api/v1")
