"""
API Routes for managing crops in a field.

This module defines the API routes for interacting with crops in a given field. It allows for
planting new crops, retrieving current crops, past crops, or all crops in a field.

Routes:
    - PUT /{field_id}/crops: Plant a new crop in the specified field.
    - GET /{field_id}/crops: Get a list of crops in the specified field with optional filters.

Dependencies:
    - get_current_user: Fetches the current authenticated user.
    - get_users_farm: Fetches the current user's farm.
    - CurrentField: Represents the specific field being referenced.
"""

from typing import Optional

from fastapi import APIRouter, status, HTTPException

from src.api.core.schema.crops.crops import CropRequest, CropsResponse
from src.api.core.dependencies import CurrentField, SessionDep
from src.api.services.crop_service import CropService

router = APIRouter(prefix="/{field_number}/crops", tags=["Crops"])


@router.put(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def plant_crop(field: CurrentField, db: SessionDep, crop_request: CropRequest, ) -> None:
    """
    Plant a crop in a field and update its ground type to match a new state e.g. growing, harvested.
    :param crop_request: the CropRequest model.
    :param db: TODO
    :param field: the current field to plant a crop in.
    """
    try:
        crop_service = CropService(db)
        await crop_service.plant_crop(current_field=field, crop_request=crop_request)
    except ValueError as exc:
        raise HTTPException(detail=str(exc), status_code=status.HTTP_400_BAD_REQUEST)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
async def get_crops(
    field: CurrentField,
    db: SessionDep,
    current: Optional[bool] = False,
    past: Optional[bool] = False
) -> CropsResponse:
    """
    Get crops planted in a field from the crop service and filter them by the possible queries.
    :param field: the current field
    :param db: TODO
    :param current: the current crop planted in the field
    :param past: the past crops that have been planted in the field.
    :return: Pydantic model showing the id, crop_type and when it was planted.
    """
    crop_service = CropService(db)

    if current:
        crops = await crop_service.get_current_crop(field)
        return CropsResponse(crops=crops, count=len(crops))

    if past:
        crops = await crop_service.get_past_crops(field)
        return CropsResponse(crops=crops, count=len(crops))

    crops = await crop_service.get_all_crops(field)
    return CropsResponse(crops=crops, count=len(crops))
