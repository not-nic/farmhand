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
from uuid import UUID
from fastapi import APIRouter, status, HTTPException

from src.api.core.dependencies import CurrentFarm
from src.api.core.logger import logger
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


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(current_farm: CurrentFarm, task_id: UUID) -> TaskResponse:
    """
    Get a singular task by its ID.
    :param current_farm: the current farm the task belongs to
    :param task_id: the UUID of the task.
    :return: a TaskResponse object with task details
    :raises: HTTPException if task is not found, or does not belong to the user.
    """
    task = TaskService.get_task_by_id(task_id)

    if not task:
        logger.info(f"Unable to find task for id: '{task_id}'...")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found."
        )

    if task.farm_id != current_farm.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Task '{task_id}' does not belong to this farm"
        )

    return TaskResponse(**task.to_dict())


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
