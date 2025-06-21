"""
Python module for initialising the database instance used in the Farmhand API.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from src.config import settings


def get_engine() -> Engine:
    """
    get the database engine from the URL.
    :return: the database engine
    """
    return create_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20)


def get_db():
    """
    Create a DB session to be used within FastAPI and repositories.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    """
    Create a DB session to be used outside the FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
