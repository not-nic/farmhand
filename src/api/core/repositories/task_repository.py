"""
Task Repository containing database interactions with the Task Model.
see: base_repository.py to see the base repository to inherit from.
"""

from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import and_

from src.api.core.repositories.base_repository import Repository

if TYPE_CHECKING:
    from src.api.core.db.models.tasks import Task


class TaskRepository(Repository):
    """
    Class containing the task repository for interacting with the Task Model.
    """

    __abstract__ = True

    @classmethod
    def get_completed_tasks(cls: "Task", farm_id: UUID) -> List["Task"]:
        """
        Get all completed tasks relating to a farm.
        :return: list of tasks.
        """
        return cls.get_session().query(cls).filter(and_(cls.completed == True and cls.farm_id == farm_id)).all()

    @classmethod
    def get_incompleted_tasks(cls: "Task", farm_id: UUID) -> List["Task"]:
        """
        Get all incomplete tasks relating to a farm.
        :return: list of tasks.
        """
        return cls.get_session().query(cls).filter(and_(cls.completed == False and cls.farm_id == farm_id)).all()
