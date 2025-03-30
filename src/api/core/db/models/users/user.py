import datetime
import uuid

from sqlalchemy import Column, UUID, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from src.api.core.repositories import UserRepository


class User(UserRepository):
    """
    Database Model for the User.

    Attributes:
        id: the UUID of the user.
        github_id: the GitHub ID of the user (only populated if signed up with GitHub OAuth).
        username: the username of the user.
        email_address: the email_address of the user.
        password: the hashed password of the user.
        name: the name of the user.
        created_at: the timestamp the user was created.
        is_active: boolean for if the user is active.

    Required fields when creating a new user: username, email_address, password, name.
    """

    __tablename__ = "users"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    github_id = Column(Integer, unique=True, nullable=True)
    username = Column(String(255), unique=True, nullable=False)
    email_address = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    farms = relationship("Farm", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User: {self.username}>"
