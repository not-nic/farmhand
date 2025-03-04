import datetime
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import Column, UUID, String, DateTime, Boolean

from src.api.core.repositories import UserRepository


class LoginRequest(BaseModel):
    """
    Model for login request
    """
    username: str
    password: str

class UserCreate(BaseModel):
    """
    Model for creating a user
    """
    username: str
    email_address: str
    password: str
    name: str


class User(UserRepository):
    """
    DB model for a user
    """
    __tablename__ = 'users'

    id = Column(UUID(), primary_key=True, default=uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email_address = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)