"""
API Routes for CRUD operations on a Farm.

This module defines the API routes for interacting with farms in the service,
everything is attached to a farm, for example fields.

Routes:
    - POST /farms: Create a new farm.
    - GET /farms: Get all farms belonging to a user
    - GET /farms/{farm_id}: get a farm by its UUID.
    - PUT /farms/{farm_id}: update a farm.
    - DELETE /farms/{farm_id} delete a farm.

Dependencies:
    - get_current_user: Fetches the current authenticated user.
    - get_user_farm: Fetches the Farm for the given farm_id.
"""

from fastapi import HTTPException, APIRouter, Depends, status

from src.api.core.repositories import MapRepository, FarmRepository
from src.api.core.schema.farms import FarmRequest, FarmUpdate, FarmResponse, FarmsResponse
from src.api.core.db.models.maps import Map
from src.api.core.db.models.farms import Farm
from src.api.core.db.models.users import User
from src.api.core.dependencies import get_current_user, get_farm, SessionDep

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "/",
    response_model=FarmResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED,
)
async def create_farm(
        farm_request: FarmRequest,
        db: SessionDep,
        current_user: User = Depends(get_current_user)
) -> FarmResponse:
    """
    Create a farm linked for the logged-in user.
    :param current_user: current logged-in user
    :param db: TODO
    :param farm_request: farm request model
    :return: (FarmResponse) Return a response of the farm
    """
    map_repository = MapRepository(db)
    farm_repository = FarmRepository(db)
    if farm_request.map_id:
        map: Map = map_repository.get_by_id(farm_request.map_id)

        if not map:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

        farm_request.map_name = map.name

    farm: Farm = farm_repository.create(
        name=farm_request.name,
        description=farm_request.description,
        map_name=farm_request.map_name,
        owner_id=current_user.id,
        map_id=farm_request.map_id,
        farm_type=farm_request.farm_type,
        difficulty=farm_request.difficulty
    )

    return FarmResponse(**farm.to_dict())


@router.get(
    "/",
    response_model=FarmsResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_farms(
        current_user: User = Depends(get_current_user)
) -> FarmsResponse:
    """
    Get all farms associated to the current logged-in user.
    :param db: TODO
    :param current_user: the current logged-in user.
    :return: (FarmsResponse) - Response of farm information and count
    """
    farms = [FarmResponse(**farm.to_dict()) for farm in current_user.farms]
    farms_count = len(farms)
    return FarmsResponse(farms=farms, count=farms_count)


@router.get(
    "/{id}",
    response_model=FarmResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_farm_by_id(
        db: SessionDep,
        farm: Farm = Depends(get_farm)
) -> FarmResponse:
    """
    Get all farms associated to the current logged-in user.
    :param db: TODO
    :param farm: farm from dependency
    :return: (FarmsResponse) - Response of farm information and count
    """
    return FarmResponse(**farm.to_dict())


@router.put(
    "/{id}", dependencies=[Depends(get_current_user)], status_code=status.HTTP_204_NO_CONTENT
)
async def update_farm(
        db: SessionDep,
        farm_update: FarmUpdate,
        farm: Farm = Depends(get_farm)
) -> None:
    """
    Update a farm for the current logged-in user.
    :param farm_update: Farm update model
    :param farm: The farm fetched by the dependency
    :return: No Content
    """
    farm_repository = FarmRepository(db)
    update_data = farm_update.model_dump(exclude_unset=True)
    farm_repository.update(farm.id, **update_data)


@router.delete(
    "/{id}", dependencies=[Depends(get_current_user)], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_farm(db: SessionDep, farm: Farm = Depends(get_farm)) -> None:
    """
    Delete a farm by its ID.
    :return: No Content
    """
    farm_repository = FarmRepository(db)
    farm_repository.delete(farm.id)
