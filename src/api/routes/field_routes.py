
from fastapi import HTTPException, APIRouter, Depends, status

from src.api.core.db_models import Field, Farm, BaseField, PrecisionFarmingField
from src.api.core.models import FieldRequest, FieldResponse, FieldsResponse
from src.api.deps import get_current_user, get_users_farm
from src.api.utils import logger, is_base_game_field, is_precision_farming_field

router = APIRouter(prefix="/{id}/fields", tags=["fields"])


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK
)
async def get_fields(current_farm: Farm = Depends(get_users_farm)) -> FieldsResponse:
    """
    Get all fields associated with a farm.
    :param current_farm: the farm for the logged-in user
    :return: (FieldsResponse) of field information and amount of fields.
    """
    fields = [FieldResponse(**Field.get_field_details(field.id)) for field in current_farm.fields]
    fields_count = len(fields)
    return FieldsResponse(fields=fields, count=fields_count)


@router.post(
    "/",
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED
)
async def create_field(field_request: FieldRequest, current_farm: Farm = Depends(get_users_farm)) -> dict:
    """
    Create a field based on the current farm type.
    Precision Farm's cannot create a 'Base' field and vice versa.
    :param current_farm: the id of the farm in the request
    :param field_request: the field request object.
    """

    if is_base_game_field(field_request, current_farm):
        logger.info(f"Creating base game field for farm: {current_farm.id}")
        field = BaseField.create(
            **field_request.model_dump(exclude_none=True),
            farm_id=current_farm.id
        )
    elif is_precision_farming_field(field_request, current_farm):
        logger.info(f"Creating precision farming field for farm: {current_farm.id}")
        field = PrecisionFarmingField.create(
            **field_request.model_dump(exclude_none=True),
            farm_id=current_farm.id
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attempted to create a {field_request.field_type} on a {current_farm.farm_type} farm."
        )

    field_details = Field.get_field_details(field.id)
    return FieldResponse(**field_details).model_dump(exclude_none=True)
