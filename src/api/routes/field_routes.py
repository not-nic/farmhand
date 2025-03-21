from typing import Union
from uuid import UUID

from fastapi import HTTPException, APIRouter, Depends, status

from src.api.core.db_models import Farm, Field
from src.api.core.models import FieldRequest, FieldsResponse, PrecisionFarmingFieldModel, \
    BaseGameFieldModel, FieldUpdate
from src.api.deps import get_current_user, get_users_farm, CurrentField
from src.api.services.field_service import FieldService

router = APIRouter(prefix="/{id}/fields", tags=["Fields"])
field_service = FieldService()


@router.post("/", dependencies=[Depends(get_current_user)], status_code=status.HTTP_201_CREATED)
async def create_field(
        field_request: FieldRequest,
        current_farm: Farm = Depends(get_users_farm)
) -> Union[BaseGameFieldModel, PrecisionFarmingFieldModel]:
    """
    Create a field based on the current farm type.
    Precision Farm's cannot create a 'Base' field and vice versa.
    :param current_farm: the id of the farm in the request
    :param field_request: the field request object.
    """
    try:
        return field_service.create_field_by_field_type(field_request, current_farm)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.get("/", dependencies=[Depends(get_current_user)], status_code=status.HTTP_200_OK)
async def get_fields(
    current_farm: Farm = Depends(get_users_farm),
) -> FieldsResponse:
    """
    Get all fields associated with a farm.
    :param current_farm: the farm for the logged-in user
    :return: (FieldsResponse) of field information and amount of fields.
    """
    fields = []
    for field in current_farm.fields:
        field_model_inst = field_service.get_field_details(field)
        fields.append(field_model_inst.model_dump(exclude_none=True))

    fields_count = len(fields)
    return FieldsResponse(fields=fields, count=fields_count).model_dump(exclude_none=True)


@router.get(
    "/{field_id}",
    dependencies=[Depends(get_current_user), Depends(get_users_farm)],
    status_code=status.HTTP_200_OK
)
async def get_field_by_id(field: CurrentField) -> Union[PrecisionFarmingFieldModel, BaseGameFieldModel]:
    """
    Get a field by its id.
    :param field: the field to get all details for
    :return: Pydantic PrecisionFarmingField or BaseFieldModel
    """
    return field_service.get_field_details(field)


@router.put(
    "/{field_id}",
    dependencies=[Depends(get_current_user), Depends(get_users_farm)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_field(field_update: FieldUpdate, field_id: UUID):
    """
    Update a field by its id.
    :param field_update: the update field request model
    :param field_id: the id of the field
    """
    update_data = field_update.model_dump(exclude_unset=True)
    Field.update(field_id, **update_data)
