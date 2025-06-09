"""
Entrypoint for starting the application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware

from src.api.fixtures.fixtures import Fixtures
from src.api.routes import api_router
from src.api.utils import format_pydantic_errors
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Functions that can be run on the startup and teardown
    of an application.
    :param app: the FastAPI application instance
    """
    Fixtures.create_service_user()
    await Fixtures.create_crop_data()
    yield  # Continue running the app


app = FastAPI(title=f"{settings.PROJECT_NAME}-{settings.VERSION}", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Exception handler for pydantic validation errors to return a standard format:
        '{"detail": "error message"}'
    :param request: FastAPI Request object
    :param exc: the pydantic validation error
    :return: a new JSON response of a formatted pydantic error.
    """
    error = format_pydantic_errors(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error)
    )
