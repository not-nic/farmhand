import uuid

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import UUID, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.api.core.db.models._model_base import SqlAlchemyBase

if TYPE_CHECKING:
    from src.api.core.db.models import Farm


class User(SqlAlchemyBase):
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

    id: Mapped[UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    github_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    farms: Mapped[list["Farm"]] = relationship("Farm", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User: {self.username}>"
