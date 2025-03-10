import uuid
import datetime

from sqlalchemy import Column, UUID, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.api.core.repositories import UserRepository, Repository


class User(UserRepository):
    """
    DB model for a user
    """

    __tablename__ = "users"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email_address = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    farms = relationship("Farm", back_populates="user", cascade="all, delete")

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
    map_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    owner_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    map_id = Column(UUID(), ForeignKey("maps.id"), nullable=True)

    user = relationship("User", back_populates="farms")

    map = relationship("Map", back_populates="farms")

    def __repr__(self):
        return f"<Farm: {self.name}, Map: {self.map_name}>"


class Map(Repository):
    """
    DB Model for Maps.
    """

    __tablename__ = "maps"

    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    author = Column(String(100), nullable=True)
    release_date = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    farms = relationship("Farm", back_populates="map")
