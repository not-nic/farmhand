"""
API Routes for CRUD operations relating to a field.

This module defines the API routes for integrating with fields
associated with a users farm.

Routes:
    - POST /fields: Create a new field.
    - GET /fields: Get all fields belonging to a farm and apply any filters such as getting fields by
      the same growing crop.
    - GET /fields/{field_number}: get a field by its number and apply any filters such as show_crops.
    - PUT /fields/{field_number}: update a field.
    - DELETE /fields/{field_number} delete a field.

Dependencies:
    - get_current_user: Fetches the current authenticated user.
    - get_user_farm: Fetches the Farm for the given field_number.
    - CurrentField: Fetches the Field for the given field_id.
"""

from typing import Optional

from fastapi import HTTPException, APIRouter, Depends, status

from src.api.core.db.models.farms import Farm
from src.api.core.schema.fields import FieldRequest, FieldUpdate
from src.api.core.dependencies import get_current_user, get_farm, CurrentField, SessionDep
from src.api.services.field_service import FieldService

router = APIRouter(prefix="/farms/{id}/fields", tags=["Fields"])


@router.post("/", dependencies=[Depends(get_current_user)], status_code=status.HTTP_201_CREATED)
async def create_field(
    db: SessionDep, field_request: FieldRequest, current_farm: Farm = Depends(get_farm)
) -> dict:
    """
    Create a field based on the current farm type.
    Precision Farm's cannot create a 'Base' field and vice versa.
    :param db: database session dependency
    :param current_farm: the id of the farm in the request
    :param field_request: the field request object.
    """
    try:
        field_service = FieldService(db)
        return field_service.create_field_by_field_type(field_request, current_farm).model_dump(
            exclude_none=True
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/", dependencies=[Depends(get_current_user)], status_code=status.HTTP_200_OK)
async def get_fields(
    db: SessionDep,
    current_farm: Farm = Depends(get_farm),
    show_crop: Optional[bool] = False,
    crop_type: Optional[str] = None,
) -> dict:
    """
    Get all fields associated with a farm.
    :param db: database session dependency
    :param current_farm: the farm for the logged-in user
    :param show_crop: Show crops planted in the fields
    :param crop_type: The type of crop to filter fields by
    :return: (FieldsResponse) of field information and amount of fields.
    """
    try:
        field_service = FieldService(db)
        return await field_service.get_all_fields(current_farm, show_crop, crop_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{field_number}",
    dependencies=[Depends(get_current_user), Depends(get_farm)],
    status_code=status.HTTP_200_OK,
)
async def get_field_by_field_number(
    field: CurrentField, db: SessionDep, show_crop: Optional[bool] = False
) -> dict:
    """
    Get a field by its number.
    :param field: the field to get all details for
    :param db: database session dependency
    :param show_crop: Show crops in the response from the service.
    :return: Pydantic PrecisionFarmingField or BaseFieldModel
    """

    field_service = FieldService(db)
    return field_service.get_field_details(field, show_crop).model_dump(exclude_none=True)


@router.put(
    "/{field_number}",
    dependencies=[Depends(get_current_user), Depends(get_farm)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_field(db: SessionDep, field: CurrentField, field_update: FieldUpdate):
    """
    Update a field by its id.
    :param db: database session dependency
    :param field_update: the update field request model
    :param field: the field to update
    """
    field_service = FieldService(db)
    field_service.update_field(field, field_update)


@router.delete(
    "/{field_number}",
    dependencies=[Depends(get_current_user), Depends(get_farm)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_field(db: SessionDep, field: CurrentField):
    """
    Delete a field and its associated field type by its id.
    :param db: database session dependency
    :param field: the field to delete
    """
    field_service = FieldService(db)
    field_service.delete_field(field)
