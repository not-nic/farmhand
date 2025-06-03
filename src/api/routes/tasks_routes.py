"""
API Route for Tasks.

This module contains routes for interacting with the Task API for managing notes
from a users Farm.

Routes:
    - GET /tasks: Get all tasks.
    - POST /tasks: Create a new task.

Dependencies:
    - CurrentFarm: Fetches the Field for the given field_id.

"""

from typing import Optional
from fastapi import APIRouter, status

from src.api.core.dependencies import CurrentFarm
from src.api.core.schema.tasks.tasks import TaskRequest, TaskResponse, TasksResponse
from src.api.services.tasks_service import TaskService

router = APIRouter(prefix="/farms/{id}/tasks", tags=["Tasks"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_tasks(
        current_farm: CurrentFarm,
        filter_by: Optional[str] = ""
) -> TasksResponse:
    """
    Return a list of all tasks associated with a farm.
    :param current_farm: The current farm to get tasks for
    :param filter_by: filter by 'incomplete' and 'complete' tasks.
    :return: (TasksResponse) pydantic model.
    """

    task_service = TaskService()
    tasks = task_service.get_tasks(farm=current_farm, filter_by=filter_by)

    task_responses = [TaskResponse.model_validate(task) for task in tasks]
    return TasksResponse(tasks=task_responses, count=len(task_responses))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(current_farm: CurrentFarm, task: TaskRequest) -> TaskResponse:
    """
    Create a task in the database.
    :param current_farm: the current farm to create a task on.
    :param task: the TaskRequest object containing the status and content.
    :return: a new completed task.
    """
    task_service = TaskService()
    return TaskResponse(
        **task_service.create_task(**task.model_dump(), farm_id=current_farm.id).to_dict()
    )
