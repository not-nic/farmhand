"""
Task Repository containing database interactions with the Task Model.
see: base_repository.py to see the base repository to inherit from.
"""

from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.api.core.db.models import Task
from src.api.core.repositories.base_repository import Repository


class TaskRepository(Repository[Task]):
    """
    Class containing the task repository for interacting with the Task Model.
    """

    def __init__(self, db: Session):
        super().__init__(db, Task)

    def get_completed_tasks(self, farm_id: UUID) -> list[type[Task]]:
        """
        Get all completed tasks relating to a farm.
        :return: list of tasks.
        """
        return (
            self.db.query(Task)
            .filter(Task.completed.is_(True), and_(Task.farm_id == farm_id))
            .all()
        )

    def get_incompleted_tasks(self, farm_id: UUID) -> list[type[Task]]:
        """
        Get all incomplete tasks relating to a farm.
        :return: list of tasks.
        """
        return (
            self.db.query(Task)
            .filter(Task.completed.is_(False), and_(Task.farm_id == farm_id))
            .all()
        )
