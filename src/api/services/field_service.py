from typing import Union, Optional
from uuid import UUID

from src.api.constants import FieldTypes, FarmTypes
from src.api.core.db_models import BaseGameField, PrecisionFarmingField, Farm, Field
from src.api.core.models import BaseGameFieldModel, PrecisionFarmingFieldModel, FieldRequest, FieldUpdate
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
        Create a field based on the current farm type.
        Precision Farm's cannot create a 'Base' field and vice versa.
        :param current_farm: the id of the farm in the request
        :param field_request: the field request object.
        :return: Pydantic Model for Base Game Field, Precision Farming Field
        """

        if self._is_base_game_field(field_request, current_farm):
            logger.info(f"Creating base game field for farm: {current_farm.name} ({current_farm.id})")

            return self._create_base_game_field(field_request, current_farm.id)
        elif self._is_precision_farming_field(field_request, current_farm):
            logger.info(f"Creating precision farming field for farm: {current_farm.name} ({current_farm.id})")

            return self._create_precision_farming_field(field_request, current_farm.id)
        else:
            raise ValueError(f"Cannot create a {field_request.field_type} on a {current_farm.farm_type} farm.")

    @staticmethod
    def get_field(field_id: UUID) -> Optional[Field]:
        """
        Get the field from the database and raise an error it doesn't exist
        :param field_id: the id of the field to retrieve
        :return: the field if it exists.
        """
        field = Field.get(field_id)
        if not field:
            raise ValueError("Field not found")
        return field

    @staticmethod
    def get_field_details(field: Field) -> Optional[Union[BaseGameFieldModel, PrecisionFarmingFieldModel]]:
        """
        Get the Pydantic model of field details for a requested field.
        :param field: The field to get the details from.
        :return: Pydantic model of the field.
        """
        if field.field_type == FieldTypes.PRECISION_FARMING_FIELD:
            return PrecisionFarmingFieldModel(**field.get_field_details())

        if field.field_type == FieldTypes.BASE_FIELD:
            return BaseGameFieldModel(**field.get_field_details())

    @staticmethod
    def _is_base_game_field(field_request: FieldRequest, current_farm: Farm) -> bool:
        """
        Helper function to check if the request is for creating a base game field on a base game farm.
        """
        return (field_request.field_type == FieldTypes.BASE_FIELD and
                current_farm.farm_type == FarmTypes.BASE)

    @staticmethod
    def _is_precision_farming_field(field_request: FieldRequest, current_farm: Farm) -> bool:
        """
        Helper function to check if the request is creating a precision farming field
        """
        return (field_request.field_type == FieldTypes.PRECISION_FARMING_FIELD and
                current_farm.farm_type == FarmTypes.PRECISION_FARMING)

    @staticmethod
    def _create_base_game_field(field_request: FieldRequest, farm_id: UUID) -> BaseGameFieldModel:
        """
        Helper Function to create a Precision Farming field.
        :param field_request: the FieldRequest Object
        :param farm_id: the current farm id
        :return: A pydantic BaseGameField model
        """
        field = Field.create(
            **field_request.model_dump(exclude_none=True, exclude={"fertilized", "limed"}),
            farm_id=farm_id
        )

        base_game_field = BaseGameField.create(
            id=field.id,
            fertilized=field_request.fertilized,
            limed=field_request.limed
        )

        field.base_game_field = base_game_field
        return BaseGameFieldModel(**field.get_field_details())

    @staticmethod
    def _create_precision_farming_field(field_request: FieldRequest, farm_id: UUID) -> PrecisionFarmingFieldModel:
        """
        Helper Function to create a Precision Farming field.
        :param field_request: the FieldRequest Object
        :param farm_id: the current farm id
        :return: A pydantic PrecisionFarmingField model
        """
        field = Field.create(
            **field_request.model_dump(exclude_none=True, exclude={"nitrogen_level", "ph_level", "soil_type"}),
            farm_id=farm_id
        )

        precision_farming_field = PrecisionFarmingField.create(
            id=field.id,
            nitrogen_level=field_request.nitrogen_level,
            ph_level=field_request.ph_level,
            soil_type=field_request.soil_type
        )

        field.precision_farming_field = precision_farming_field
        return PrecisionFarmingFieldModel(**field.get_field_details())
