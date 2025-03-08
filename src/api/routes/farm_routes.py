from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from src.api.core.models import FarmCreate, FarmResponse, User, Farm, FarmsResponse, FarmUpdate
from src.api.deps import get_current_user, get_users_farm

router = APIRouter(prefix="/farm", tags=["farms"])

@router.post(
    "/",
    response_model=FarmResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED
)
async def create_farm(farm_request: FarmCreate, current_user: User = Depends(get_current_user)):
    """
    Create a farm linked for the logged-in user.
    :param current_user: current logged-in user
    :param farm_request: farm request model
    :return: (FarmResponse) Return a response of the farm
    """
    farm = Farm.create(
        name=farm_request.name,
        description=farm_request.description,
        map=farm_request.map,
        owner_id=current_user.id
    )

    return FarmResponse(**farm.to_dict())

@router.get(
    "/",
    response_model=FarmsResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK
)
async def get_farms(current_user: User = Depends(get_current_user)):
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
    status_code=status.HTTP_200_OK
)
async def get_farm_by_id(farm: Farm = Depends(get_users_farm)):
    """
    Get all farms associated to the current logged-in user.
    :param farm: farm from dependency
    :return: (FarmsResponse) - Response of farm information and count
    """
    return FarmResponse(**farm.to_dict())

@router.put(
    "/{id}",
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_farm(farm_update: FarmUpdate, farm: Farm = Depends(get_users_farm)):
    """
    Update a farm for the current logged-in user.
    :param farm_update: Farm update model
    :param farm: The farm fetched by the dependency
    :return: No Content
    """
    update_data = farm_update.model_dump(exclude_unset=True)
    farm.update(farm.id, **update_data)

    return FarmResponse(**farm.to_dict())

@router.delete(
    "/{id}",
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_farm(farm: Farm = Depends(get_users_farm)):
    """
    Delete a farm by its ID.
    :return: No Content
    """
    Farm.delete(farm.id)
