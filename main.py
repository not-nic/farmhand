"""
Entrypoint for starting the application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.fixtures.fixtures import Fixtures
from src.api.routes import api_router
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Fixtures.create_service_user()
    yield  # Continue running the app


app = FastAPI(title=f"{settings.PROJECT_NAME}-{settings.VERSION}", lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_V1_STR)

