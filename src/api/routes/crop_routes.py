from fastapi import APIRouter, Depends, status

from src.api.core.models import CropRequest
from src.api.deps import CurrentField, get_current_user, get_users_farm
from src.api.services.crop_service import CropService

router = APIRouter(prefix="/{field_id}/crops", tags=["Crops"])
crop_service = CropService()


@router.put(
    "",
    dependencies=[Depends(get_current_user), Depends(get_users_farm)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def plant_crop(crop_request: CropRequest, field: CurrentField) -> None:
    crop_service.plant_crop(crop_request, field)
