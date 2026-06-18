"""
API Routes for CRUD operations on a Farm.

This module defines the API routes for interacting with farms in the service.
Most routes in the API are extended from the farm e.g. Fields, Tasks, etc.

Routes:
    - POST /farms: Create a new farm.
    - GET /farms: Get all farms belonging to a user
    - GET /farms/{farm_id}: get a farm by its UUID.
    - PATCH /farms/{farm_id}: update a farm.
    - DELETE /farms/{farm_id} delete a farm.

Dependencies:
    - CurrentUser: Fetches the current authenticated user.
    - CurrentFarm: Fetches the Farm for the given farm_id.
"""

from fastapi import APIRouter, HTTPException, status

from src.api.core.dependencies import CurrentFarm, CurrentUser, SessionDep
from src.api.core.repositories import FarmRepository
from src.api.core.schema.farms import FarmRequest, FarmResponse, FarmsResponse, FarmUpdate
from src.api.core.schema.maps.maps import MapModel
from src.api.exceptions.farmhand_data_api_exceptions import ServiceUnavailableError
from src.api.services.data_service import DataApiService
from src.api.services.farm_service import FarmService

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "/",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_farm(
    farm_request: FarmRequest, db: SessionDep, current_user: CurrentUser
) -> FarmResponse:
    """
    Create a farm for a user.
    :param current_user: The current user.
    :param db: Database session dependency.
    :param farm_request: Farm request object.
    :return: (FarmResponse) Farm response object.
    """
    farm_service = FarmService(db)
    try:
        new_farm = await farm_service.create_farm(
            farm_request.map_id,
            farm_request.farm_type,
            farm_request.difficulty,
            current_user
        )
        return FarmResponse(**new_farm.to_dict())
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to communicate with farmhand-data-api."
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Map not found."
        )


@router.get(
    "/",
    response_model=FarmsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_farms(current_user: CurrentUser, db: SessionDep) -> FarmsResponse:
    """
    Get all farms for a given user.
    :param current_user: (User) The current user.
    :param db: A database session.
    :return: (Farms) a list of Farms.
    """
    farm_service = FarmService(db)
    farms = farm_service.get_farms(current_user)
    return FarmsResponse(
        farms=farms,
        count=len(farms),
    )


@router.get(
    "/{id}",
    response_model=FarmResponse,
    status_code=status.HTTP_200_OK,
)
async def get_farm_by_id(farm: CurrentFarm) -> FarmResponse:
    """
    Get a farm by its ID for the current user.
    :param farm: Dependency for the Current Farm.
    :return: (Farm) the farm object.
    """
    return FarmResponse.model_validate(farm)


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_farm(
    db: SessionDep,
    farm: CurrentFarm,
    farm_update: FarmUpdate,
) -> None:
    """
    Update a farm with a new name or description.
    :param db: A database session.
    :param farm: Dependency for the Current Farm.
    :param farm_update: (Farm) update model.
    """
    FarmService(db).update_farm(
        farm=farm,
        name=farm_update.name,
        description=farm_update.description,
        difficulty=farm_update.difficulty,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(db: SessionDep, farm: CurrentFarm) -> None:
    """
    Delete a farm by its ID.
    :param db: database session dependency.
    :param farm: Farm dependency.
    :return: No Content
    """
    FarmService(db).delete_farm(farm)
