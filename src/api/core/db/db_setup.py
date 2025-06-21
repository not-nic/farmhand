"""
Python module for initialising the database instance used in the Farmhand API.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings


def get_engine() -> Engine:
    """
    get the database engine from the URL.
    :return: the database engine
    """
    return create_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20)


def _get_db() -> Generator[Session, None, None]:
    """
    Internal generator for DB session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db = _get_db
db_session = contextmanager(_get_db)
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
