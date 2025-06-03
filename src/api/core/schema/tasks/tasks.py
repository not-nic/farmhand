"""
Python module containing pydantic models for Tasks.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class TaskRequest(BaseModel):
    """
    Request model for creating a new task.
    """

    content: str
    completed: bool


class TaskResponse(BaseModel):
    """
    Response model for a singular task.
    """

    id: UUID
    content: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TasksResponse(BaseModel):
    """
    Response Model for a list of tasks.
    """

    tasks: list[TaskResponse]
    count: int

