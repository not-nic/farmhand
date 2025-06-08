"""
Unit Tests for the Farm API Routes.
"""
from typing import Optional
from uuid import UUID

import pytest
from fastapi import status

from src.api.core.schema.tasks.tasks import TasksResponse, TaskResponse
from src.api.services.tasks_service import TaskService
from src.config import settings
from tests.utils import TestClientHelper


@pytest.mark.usefixtures("client", "session")
class TestTaskRoutes:

    @staticmethod
    def task_url(farm_id: UUID, filter_by: Optional[str] = "", task_id: Optional[UUID] = None):
        """task url util method"""
        task_id_path = f"/{task_id}" if task_id else ""
        filter_by_query = f"?filter_by={filter_by}" if filter_by else ""
        return f"{settings.API_V1_STR}/farms/{farm_id}/tasks{task_id_path}{filter_by_query}"

    @pytest.mark.parametrize("filter", ["none", "complete", "incomplete"])
    def test_get_tasks_by_filters(self, client, session, farm, filter):
        """
        Test that tasks can be retrieved from the endpoint and filtered.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        :param filter: Filter parameter.
        """
        task_service = TaskService()
        tasks = task_service.get_tasks(farm, filter_by=filter)
        result = TestClientHelper.get(self.task_url(farm_id=farm.id, filter_by=filter), client)

        expected_task_json = TasksResponse(tasks=tasks, count=len(tasks)).model_dump(mode="json")

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["count"] == len(tasks)
        assert result.json() == expected_task_json

    def test_create_task(self, client, session, farm):
        """
        Test that a POST request to the task endpoint creates a new task.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        """
        payload = {
            "content": "New Task Content",
            "completed": False
        }

        result = TestClientHelper.post(self.task_url(farm_id=farm.id), json=payload, client=client)

        task_service = TaskService()
        task = task_service.get_task_by_id(UUID(result.json()["id"]))

        expected_task_json = TaskResponse(**task.to_dict()).model_dump(mode="json")

        assert result.status_code == status.HTTP_201_CREATED
        assert result.json() == expected_task_json

    def test_create_task_endpoint_returns_bad_request_when_too_long(self, client, session, farm):
        """
        Test that a POST request to the task endpoint with a content greater than 280 characters
        returns a 400 bad request error.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        """
        payload = {
            "content": ("A" * 281),
            "completed": False
        }

        result = TestClientHelper.post(self.task_url(farm_id=farm.id), json=payload, client=client)

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": "Tasks must be shorter than '280' characters."}

    def test_update_task(self, client, session, farm, tasks):
        """
        Test that a PUT request to the task endpoint updates it.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        """
        payload = {
            "content": "updated task content",
            "completed": True
        }

        task_id = tasks[0].id
        result = TestClientHelper.put(self.task_url(farm_id=farm.id, task_id=task_id), json=payload, client=client)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_update_task_endpoint_returns_bad_request_when_too_long(self, client, session, farm, tasks):
        """
        Test that a PUT request to the task endpoint with a content greater than 280 characters
        returns a 400 bad request error.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        payload = {
            "content": ("A" * 281),
            "completed": False
        }

        task_id = tasks[0].id

        result = TestClientHelper.put(self.task_url(farm_id=farm.id, task_id=task_id), json=payload, client=client)

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": "Tasks must be shorter than '280' characters."}

    def test_delete_task(self, client, session, farm, tasks):
        """
        Test that a POST request to the task endpoint creates a new task.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        task_id = tasks[0].id
        result = TestClientHelper.delete(self.task_url(farm_id=farm.id, task_id=task_id), client=client)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_get_task_by_id(self, client, session, farm, tasks):
        """
        Test that a task can be retrieved by its ID.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        task = tasks[0]
        result = TestClientHelper.get(self.task_url(farm_id=farm.id, task_id=task.id), client=client)

        assert result.status_code == status.HTTP_200_OK
        assert TaskResponse(**task.to_dict()).model_dump(mode="json") == result.json()

    def test_complete_task(self, client, session, farm, tasks):
        """
        Test that a task can be completed.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm: Farm Fixture.
        :param tasks: Tasks Fixture.
        """
        task = tasks[1]
        result = TestClientHelper.put(
            url=f"{self.task_url(farm_id=farm.id, task_id=task.id)}/complete",
            json={},
            client=client
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT
