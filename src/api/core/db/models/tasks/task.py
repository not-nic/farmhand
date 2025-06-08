"""
Python Module containing the Task SQLAlchemy model.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from sqlalchemy import UUID, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.core.repositories.task_repository import TaskRepository

if TYPE_CHECKING:
    from src.api.core.db.models import Farm


class Task(TaskRepository):
    """
    Database Model for a Task.

    Attributes:
        id: The UUID of the Task.
        completed: Boolean if the task has been completed or not
        content: The content of the task
        created_at: The date and time the task was created
        farm: the Farm the note is attached too.

    Required attributes to create a task: All fields.
    """

    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    content: Mapped[str] = mapped_column(String(280), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    farm_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("farms.id"), nullable=False)
    farm: Mapped["Farm"] = relationship("Farm", back_populates="tasks")

    def __repr__(self):
        return f"Task(id={self.id}, content='{self.content}, completed={self.completed}, farm_id={self.farm.id})"
