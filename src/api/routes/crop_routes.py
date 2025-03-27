"""
API Routes for Crops.
"""
from typing import Optional

from fastapi import APIRouter, Depends, status

from src.api.core.models import CropRequest, CropResponse
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
    crop_service.plant_crop(current_field=field, crop_request=crop_request)


@router.get(
    "",
    dependencies=[Depends(get_current_user), Depends(get_users_farm)],
    status_code=status.HTTP_200_OK
)
async def get_crops(
    field: CurrentField,
    current: Optional[bool] = False,
    past: Optional[bool] = False
) -> list[CropResponse]:
    """
    Get crops planted in a field from the crop service and filter them by the possible queries.
    :param field: the current field
    :param current: the current crop planted in the field
    :param past: the past crops that have been planted in the field.
    :return: Pydantic model showing the id, crop_type and when it was planted.
    """

    if current:
        return crop_service.get_current_crop(field)

    if past:
        return crop_service.get_past_crops(field)

    return crop_service.get_all_crops(field)


