
from fastapi import HTTPException, APIRouter, Depends, status

from src.api.core.models import FarmRequest, FarmResponse, FarmsResponse, FarmUpdate
from src.api.core.db_models import User, Farm, Map
from src.api.deps import get_current_user, get_users_farm

router = APIRouter(prefix="/farm", tags=["farms"])


@router.post(
    "/",
    response_model=FarmResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED,
)
async def create_farm(farm_request: FarmRequest, current_user: User = Depends(get_current_user)) -> FarmResponse:
    """
    Create a farm linked for the logged-in user.
    :param current_user: current logged-in user
    :param farm_request: farm request model
    :return: (FarmResponse) Return a response of the farm
    """
    if farm_request.map_id:
        map: Map = Map.get(farm_request.map_id)

        if not map:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

        farm_request.map_name = map.name

    farm = Farm.create(
        name=farm_request.name,
        description=farm_request.description,
        map_name=farm_request.map_name,
        owner_id=current_user.id,
        map_id=farm_request.map_id
    )

    return FarmResponse(**farm.to_dict())


@router.get(
    "/",
    response_model=FarmsResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_farms(current_user: User = Depends(get_current_user)) -> FarmsResponse:
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
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_farm_by_id(farm: Farm = Depends(get_users_farm)) -> FarmResponse:
    """
    Get all farms associated to the current logged-in user.
    :param farm: farm from dependency
    :return: (FarmsResponse) - Response of farm information and count
    """
    return FarmResponse(**farm.to_dict())


@router.put(
    "/{id}", dependencies=[Depends(get_current_user)], status_code=status.HTTP_204_NO_CONTENT
)
async def update_farm(farm_update: FarmUpdate, farm: Farm = Depends(get_users_farm)) -> None:
    """
    Update a farm for the current logged-in user.
    :param farm_update: Farm update model
    :param farm: The farm fetched by the dependency
    :return: No Content
    """
    update_data = farm_update.model_dump(exclude_unset=True)
    farm.update(farm.id, **update_data)


@router.delete(
    "/{id}", dependencies=[Depends(get_current_user)], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_farm(farm: Farm = Depends(get_users_farm)) -> None:
    """
    Delete a farm by its ID.
    :return: No Content
    """
    Farm.delete(farm.id)
