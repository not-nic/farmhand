"""
Python module for initialising the database instance used in the Farmhand API.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings


def _make_engine(url: str) -> Engine:
    return create_engine(url, pool_size=10, max_overflow=20)


def _make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


engine: Engine = _make_engine(settings.DATABASE_URL)
SessionLocal: sessionmaker = _make_session_factory(engine)


def get_db() -> Generator[Session]:
    """FastAPI dependency that provides a database session."""
    with SessionLocal() as session:
        yield session


@contextmanager
def db_session() -> Generator[Session]:
    """Context manager for use outside of FastAPI DI (scripts, CLI, etc.)."""
    with SessionLocal() as session:
        yield session
