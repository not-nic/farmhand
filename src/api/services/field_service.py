from typing import Union, Type
from uuid import UUID

from src.api.constants import FieldTypes, FarmTypes
from src.api.core.db_models import BaseField, PrecisionFarmingField, Farm, Field
from src.api.core.models import BaseGameFieldModel, PrecisionFarmingFieldModel, FieldRequest
from src.api.utils import logger


class FieldService:
    """
    Field Service module for field CRUD methods and any additional logic.
    """

    def create_field_by_field_type(
        self,
        field_request: FieldRequest,
        current_farm: Farm
    ) -> Union[BaseGameFieldModel, PrecisionFarmingFieldModel]:
        """

        :param field_request:
        :param current_farm:
        :return:
        """

        if self._is_base_game_field(field_request, current_farm):
            logger.info(f"Creating base game field for farm: {current_farm.id}")

            return self._create_field_and_get_details(
                field_request, current_farm.id, BaseField, BaseGameFieldModel
            )
        elif self._is_precision_farming_field(field_request, current_farm):
            logger.info(f"Creating precision farming field for farm: {current_farm.id}")

            return self._create_field_and_get_details(
                field_request, current_farm.id, PrecisionFarmingField, PrecisionFarmingFieldModel
            )
        else:
            raise ValueError(f"Attempted to create a {field_request.field_type} on a {current_farm.farm_type} farm.")

    @staticmethod
    def get_field_details(field_id: UUID) -> Union[BaseGameFieldModel, PrecisionFarmingFieldModel]:
        """
        get the Pydantic model of field details for a requested field.
        :param field_id: the ID of the field.
        :return: Pydantic model of the field.
        """

        field = Field.get(field_id)

        if not field:
            raise ValueError("Field not found")

        field_details = Field.get_field_details(field_id)

        if field.field_type == FieldTypes.PRECISION_FARMING_FIELD:
            return PrecisionFarmingFieldModel(**field_details)

        elif field.field_type == FieldTypes.BASE_FIELD:
            return BaseGameFieldModel(**field_details)

        else:
            raise ValueError("Field Type not implemented")

    @staticmethod
    def _is_base_game_field(field_request: FieldRequest, current_farm: Farm) -> bool:
        """
        Check if the request is for creating a base game field on a base game farm.
        """
        return (field_request.field_type == FieldTypes.BASE_FIELD and
                current_farm.farm_type == FarmTypes.BASE)

    @staticmethod
    def _is_precision_farming_field(field_request: FieldRequest, current_farm: Farm) -> bool:
        """
        check if the request is creating a precision farming field
        """
        return (field_request.field_type == FieldTypes.PRECISION_FARMING_FIELD and
                current_farm.farm_type == FarmTypes.PRECISION_FARMING)

    @staticmethod
    def _create_field_and_get_details(
        field_request: FieldRequest,
        farm_id: UUID,
        field_object: Type[BaseField | PrecisionFarmingField],
        field_model: [BaseGameFieldModel | PrecisionFarmingFieldModel]
    ) -> [BaseGameFieldModel | PrecisionFarmingFieldModel]:
        """
        Util function to create a field based on the field model
        :param field_model: the pydantic field model
        :param field_object: the database field object
        :param farm_id: the id for the farm
        :param field_request: The field request pydantic model
        :return: The field model object.
        """
        field = field_object.create(
            **field_request.model_dump(exclude_none=True),
            farm_id=farm_id
        )

        field_details = Field.get_field_details(field.id)
        return field_model(**field_details)
