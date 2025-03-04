from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

from src.config import config

engine = create_engine(config.DATABASE_URL)
db_session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base = declarative_base()

def create_db_and_tables():
    """
    create database tables on application startup
    """
    Base.metadata.create_all(engine)


