"""
API Routes for CRUD operations on a Farm.

This module defines the API routes for interacting with farms in the service,
everything is attached to a farm, for example fields.

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

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.core.dependencies import CurrentFarm, CurrentUser, SessionDep, get_current_user
from src.api.core.repositories import FarmRepository
from src.api.core.schema.farms import FarmRequest, FarmResponse, FarmsResponse, FarmUpdate
from src.api.core.schema.maps.maps import MapModel
from src.api.exceptions.farmhand_data_api_exceptions import ServiceUnavailableError
from src.api.services.data_service import DataApiService

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
    Create a farm linked for the logged-in user.
    :param current_user: current logged-in user
    :param db: database session dependency.
    :param farm_request: farm request model
    :return: (FarmResponse) Return a response of the farm
    """
    farm_repository = FarmRepository(db)

    if farm_request.map_id or farm_request.map_id == 0:
        try:
            data_service = DataApiService()
            map_response = await data_service.get_map_by_id(farm_request.map_id)
        except ServiceUnavailableError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to communicate with farmhand-data-api."
            )

        if not map_response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

        map = MapModel.model_validate(map_response)

        farm_request.map_name = map.name

    farm = farm_repository.create(
        name=farm_request.name,
        description=farm_request.description,
        map_name=farm_request.map_name,
        owner_id=current_user.id,
        map_id=farm_request.map_id,
        farm_type=farm_request.farm_type,
        difficulty=farm_request.difficulty,
    )

    return FarmResponse(**farm.to_dict())


@router.get(
    "/",
    response_model=FarmsResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_farms(current_user: CurrentUser) -> FarmsResponse:
    """
    Get all farms associated to the current logged-in user.
    :param current_user: the current logged-in user.
    :return: (FarmsResponse) - Response of farm information and count
    """
    farms = [FarmResponse(**farm.to_dict()) for farm in current_user.farms]
    farms_count = len(farms)
    return FarmsResponse(farms=farms, count=farms_count)


@router.get(
    "/{id}",
    response_model=FarmResponse,
    status_code=status.HTTP_200_OK,
)
async def get_farm_by_id(farm: CurrentFarm) -> FarmResponse:
    """
    Get all farms associated to the current logged-in user.
    :param farm: farm from dependency
    :return: (FarmsResponse) - Response of farm information and count
    """
    return FarmResponse(**farm.to_dict())


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_farm(
    db: SessionDep, farm_update: FarmUpdate, farm: CurrentFarm
) -> None:
    """
    :param db: database session dependency.
    :param farm_update: Farm update model
    :param farm: The farm fetched by the dependency
    :return: No Content
    """
    farm_repository = FarmRepository(db)

    if farm_update.map_id:
        try:
            data_service = DataApiService()
            map_response = await data_service.get_map_by_id(farm_update.map_id)
        except ServiceUnavailableError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to communicate with farmhand-data-api."
            )

        if not map_response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

        map = MapModel.model_validate(map_response)

        farm_update.map_name = map.name
        farm_repository.update(farm.id, **farm_update.model_dump(exclude_unset=True))

    farm_repository.update(farm.id, **farm_update.model_dump(exclude_unset=True))


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_farm(db: SessionDep, farm: CurrentFarm) -> None:
    """
    Delete a farm by its ID.
    :param db: database session dependency.
    :param farm: Farm dependency.
    :return: No Content
    """
    farm_repository = FarmRepository(db)
    farm_repository.delete(farm.id)
