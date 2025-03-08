import datetime
import uuid
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, UUID, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.api.core.repositories import UserRepository, Repository


class LoginRequest(BaseModel):
    """
    Request model for logging into the service.
    """
    username: str
    password: str


class UserCreate(BaseModel):
    """
    Request model for creating a new user.
    """
    username: str
    email_address: str
    password: str
    name: str


class FarmCreate(BaseModel):
    """
    Request model for creating a farm.
    """
    name: str
    description: str
    map: str


class FarmUpdate(FarmCreate):
    """
    Request model for creating a farm.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    map: Optional[str] = None

class FarmResponse(BaseModel):
    """
    Response model for returning a singular farm.
    """
    id: uuid.UUID
    name: str
    map: str
    description: str
    created_at: datetime.datetime



class FarmsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """
    farms: list[FarmResponse]
    count: int


class User(UserRepository):
    """
    DB model for a user
    """
    __tablename__ = 'users'

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email_address = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    farms = relationship(
        'Farm',
        back_populates='user',
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User: {self.username}>"


class Farm(Repository):
    """
    DB Model for farms.
    """
    __tablename__ = 'farms'

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    map = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    owner_id = Column(UUID(), ForeignKey('users.id'), nullable=False)

    user = relationship(
        'User',
        back_populates='farms'
    )

    def __repr__(self):
        return f"<Farm: {self.name}>"
