"""
Python module for initialising the database instance used in the Farmhand API.
"""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from src.config import settings


def get_engine() -> Engine:
    """
    get the database engine from the URL.
    :return: the database engine
    """
    return create_engine(settings.DATABASE_URL)


def get_session():
    """
    Create a scoped DB session.
    """
    return scoped_session(sessionmaker(autoflush=True, bind=engine))


engine = get_engine()
db_session = get_session()
Base = declarative_base()
