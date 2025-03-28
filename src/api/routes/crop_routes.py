"""
API Routes for Crops.
"""
from typing import Optional

from fastapi import APIRouter, Depends, status, HTTPException

from src.api.core.models import CropRequest, CropsResponse
from src.api.deps import CurrentField, get_current_user, get_users_farm
from src.api.services.crop_service import CropService

router = APIRouter(prefix="/{field_id}/crops", tags=["Crops"])
crop_service = CropService()


@router.put(
    "",
    dependencies=[Depends(get_current_user), Depends(get_users_farm)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def plant_crop(field: CurrentField, crop_request: CropRequest) -> None:
    """
    Plant a crop in a field by providing a field and Crop and a Fround type.
    :param crop_request:
    :param field:
    """
    try:
        crop_service.plant_crop(current_field=field, crop_request=crop_request)
    except ValueError as exc:
        raise HTTPException(
            detail=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get(
    "",
    dependencies=[Depends(get_current_user), Depends(get_users_farm)],
    status_code=status.HTTP_200_OK
)
async def get_crops(
    field: CurrentField,
    current: Optional[bool] = False,
    past: Optional[bool] = False
) -> CropsResponse:
    """
    Get crops planted in a field from the crop service and filter them by the possible queries.
    :param field: the current field
    :param current: the current crop planted in the field
    :param past: the past crops that have been planted in the field.
    :return: Pydantic model showing the id, crop_type and when it was planted.
    """

    if current:
        crops = crop_service.get_current_crop(field)
        return CropsResponse(crops=crops, count=len(crops))

    if past:
        crops = crop_service.get_past_crops(field)
        return CropsResponse(crops=crops, count=len(crops))

    crops = crop_service.get_all_crops(field)
    return CropsResponse(crops=crops, count=len(crops))


