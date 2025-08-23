"""
Python module containing pydantic models for Tasks.
"""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, StringConstraints


class TaskRequest(BaseModel):
    """
    Request model for creating a new task.
    """

    content: Annotated[str, StringConstraints(min_length=10, max_length=280, strip_whitespace=True)]
    completed: bool = False


class TaskUpdate(BaseModel):
    """
    Request model for updating a task.
    """

    content: Optional[Annotated[str, StringConstraints(min_length=10, max_length=280, strip_whitespace=True)]] = None
    completed: Optional[bool] = False


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
