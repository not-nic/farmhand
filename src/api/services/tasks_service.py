"""
Python module containing the TaskService used for creating and managing tasks in the
farmhand service.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from src.api.core.db.models import Farm, Task
from src.api.core.logger import logger
from src.api.core.repositories import TaskRepository


class TaskService:
    """
    Task Service Class for creating, retrieving and managing users tasks.
    """

    def __init__(self, db: Session):
        self.MAX_TASK_LENGTH = 280
        self.db = db
        self.task_repository = TaskRepository(db)

    def get_tasks(self, farm: Farm, filter_by: str | None = "") -> list[type[Task]] | list[Task]:
        """
        Get all task associated to a farm, filtered by either complete or not.
        :param farm: (Farm) the farm to get tasks from.
        :param filter_by: (str) filter by complete or incomplete tasks.
        :return: List of Tasks.
        """
        logger.info(
            f"[Task Service]: Retrieving tasks for farm: '{farm.id}' - filtered by: {filter_by}"
        )

        if filter_by.lower() == "complete":
            return self.task_repository.get_completed_tasks(farm_id=farm.id)

        if filter_by.lower() == "incomplete":
            return self.task_repository.get_incompleted_tasks(farm_id=farm.id)

        return farm.tasks

    def create_task(self, content: str, completed: bool, farm_id: UUID) -> Task:
        """
        Create a new task tied to a farm.
        :param content: (str) the content of the task.
        :param completed: (bool) if the task is completed.
        :param farm_id: (UUID) the ID of the farm of the farm that the note belong too.
        :return: (Task) Task database object.
        """
        logger.info(f"[Task Service]: Creating new task for farm: '{farm_id}'...")

        self._check_task_length(content)

        return self.task_repository.create(content=content, completed=completed, farm_id=farm_id)

    def get_task_by_id(self, task_id: UUID) -> Task | None:
        """
        Get a Task by its UUID.
        :param task_id: (uuid) the ID of the task.
        :return: (Task) if it exists.
        """
        logger.info(f"[Task Service]: Getting Task: '{task_id}'")
        return self.task_repository.get_by_id(task_id)

    def delete_task(self, task: Task) -> None:
        """
        Delete a task by its UUID.
        :param task: (uuid) the Task object.
        """
        logger.info(f"[Task Service]: Deleting Task: '{task.id}'")
        self.task_repository.delete(task)

    def update_task(
        self, task: Task, content: str | None = None, completed: bool | None = None
    ) -> None:
        """
        Update a task by its content or completed status.
        :param task: the ID of the task to update.
        :param content: the new content to update an existing task
        :param completed: the new status of the task.
        :return: (Task) the updated task.
        """
        update_fields = {}

        if content is not None:
            self._check_task_length(content)
            update_fields["content"] = content
        if completed is not None:
            update_fields["completed"] = completed

        if update_fields:
            logger.info(f"[Task Service]: Updating Task: '{task.id}' with new content or status.")
            self.task_repository.update(obj=task, **update_fields)

    def _check_task_length(self, content: str) -> bool:
        """
        check the length of the task content
        :param content: the content to check.
        :return: (bool) if the task length is under the max task length.
        :raises: ValueError if task is too long.
        """
        if len(content) > self.MAX_TASK_LENGTH:
            raise ValueError(f"Tasks must be shorter than '{self.MAX_TASK_LENGTH}' characters.")
        return True
