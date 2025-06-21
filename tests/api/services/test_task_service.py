"""
Task Service unit tests
"""

import copy
import pytest

from uuid import UUID

from src.api.core.repositories import TaskRepository
from src.api.services.tasks_service import TaskService


@pytest.mark.usefixtures("db", "unit_test_user", "tasks")
class TestTaskService:
    def test_create_task(self, db, farm):
        """
        Test that a task can be created and when retrieved
        it is the same as the created task.
        :param farm: Farm Fixture.
        """
        task_service = TaskService(db)
        new_task = task_service.create_task("new task data", completed=False, farm_id=farm.id)
        task_repository = TaskRepository(db)
        db_task = task_repository.get_by_id(new_task.id)

        assert new_task is db_task

    def test_create_task_with_too_much_content(self, db, farm):
        """
        Test that a ValueError is raised when a task's content is > MAX_TASK_LENGTH
        :param farm: Farm Fixture.
        """
        with pytest.raises(ValueError, match="Tasks must be shorter than '280' characters."):
            task_service = TaskService(db)
            task_service.create_task(content=("A" * 281), completed=False, farm_id=farm.id)

    def test_get_tasks(self, db, farm, tasks):
        """
        Test that multiple tasks can be retrieved.
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        task_service = TaskService(db)

        task_service.create_task(
            "different farm task",
            completed=False,
            farm_id=UUID("3ba72831-2faa-4fae-87b2-6a4cbab16b34"),
        )

        tasks = task_service.get_tasks(farm)

        assert len(tasks) == 3

    def test_filter_complete_tasks(self, db, farm, tasks):
        """
        Test that multiple tasks can be retrieved and filtered to only 'complete' tasks.
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        task_service = TaskService(db)
        tasks = task_service.get_tasks(farm, filter_by="complete")
        assert len(tasks) == 1

    def test_filter_incomplete_tasks(self, db, farm, tasks):
        """
        Test that multiple tasks can be retrieved and filtered to only 'incomplete' tasks.
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        task_service = TaskService(db)
        tasks = task_service.get_tasks(farm, filter_by="incomplete")
        assert len(tasks) == 2

    def test_get_task_by_id(self, db, farm):
        """
        Test getting a task by its ID.
        :param farm: Farm Fixture.
        :return:
        """
        task_service = TaskService(db)
        task = task_service.create_task("new task data", completed=False, farm_id=farm.id)
        db_task = task_service.get_task_by_id(task.id)

        assert task is db_task

    def test_update_task(self, db, farm):
        """
        test that a task can be updated the content is not the same.
        :param farm: Farm Fixture
        :return:
        """
        task_service = TaskService(db)
        task = task_service.create_task("new task", completed=False, farm_id=farm.id)

        original_task = copy.deepcopy(task_service.get_task_by_id(task.id))

        task_service.update_task(task.id, content="updated task", completed=True)

        updated_task = task_service.get_task_by_id(task.id)

        assert original_task.content != updated_task.content
        assert original_task.completed != updated_task.completed

    def test_complete_task(self, db, farm):
        """
        Test that a task can be completed.
        :param farm: Farm Fixture.
        """
        task_service = TaskService(db)
        task = task_service.create_task("new task", completed=False, farm_id=farm.id)
        task_service.complete_task(task)

        assert task.completed is True

    def test_delete_task(self, db, farm):
        """
        Test that a task can be deleted.
        :param farm: Farm Fixture.
        """
        task_service = TaskService(db)
        task = task_service.create_task("new task", completed=False, farm_id=farm.id)
        task_service.delete_task(task.id)

        deleted_task = task_service.get_task_by_id(task.id)

        assert deleted_task is None
