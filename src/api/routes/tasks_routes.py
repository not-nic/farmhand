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

from src.api.core.dependencies import CurrentFarm, TaskDep
from src.api.core.schema.tasks.tasks import TaskRequest, TaskResponse, TasksResponse, TaskUpdate
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


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(task: TaskDep) -> TaskResponse:
    """
    Get a singular task by its ID.
    :param task: (Task) The task Dependency.
    :return: a TaskResponse object with task details
    :raises: HTTPException if task is not found, or does not belong to the user.
    """
    return TaskResponse(**task.to_dict())


@router.put("/{task_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_task(task: TaskDep) -> None:
    """
    Change the completed status of a task.
    :param task: (Task) The task Dependency.
    :return: 204 No content message.
    """
    TaskService.complete_task(task)


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(task: TaskDep, task_update: TaskUpdate) -> None:
    """
    Delete a task by its ID, if a task exists.
    :param task: (Task) The task Dependency.
    :param task_update: Task update request model.
    :return: 204 No content message.
    """
    TaskService.update_task(task.id, **task_update.model_dump(exclude_none=True))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task: TaskDep) -> None:
    """
    Delete a task by its ID, if a task exists.
    :param task: (Task) The task Dependency.
    :return: 204 No content message.
    """
    TaskService.delete_task(task.id)
