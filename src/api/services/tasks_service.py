"""
TODO
"""
from typing import List, Optional
from uuid import UUID

from src.api.core.db.models import Task, Farm
from src.api.core.logger import logger


class TaskService:
    """
    Task Service Class for creating, retrieving and managing users tasks.
    """

    @staticmethod
    def get_tasks(farm: Farm, filter_by: Optional[str]) -> List[Task]:
        """
        Get all task associated to a farm, filtered by either complete or not.
        :param farm: (Farm) the farm to get tasks from.
        :param filter_by: (str) filter by complete or incomplete tasks.
        :return: List of Tasks.
        """
        if filter_by.lower() == "complete":
            return Task.get_completed_tasks(farm_id=farm.id)

        if filter_by.lower() == "incomplete":
            return Task.get_incompleted_tasks(farm_id=farm.id)

        return farm.tasks

    @staticmethod
    def create_task(content: str,  completed: bool, farm_id: UUID) -> Task:
        """
        Create a new task tied to a farm.
        :param content: (str) the content of the task.
        :param completed: (bool) if the task is completed.
        :param farm_id: (UUID) the ID of the farm of the farm that the note belong too.
        :return: (Task) Task database object.
        """
        logger.info(f"Creating new task on farm: '{farm_id}'")

        return Task.create(
            content=content,
            completed=completed,
            farm_id=farm_id
        )

    def get_task_by_id(self, id: int):
        pass

    def delete_task(self, id: int):
        pass

    def update_task(self, id: int):
        pass

    def complete_task(self, id: int):
        pass

