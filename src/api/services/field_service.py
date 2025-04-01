"""
Field Service Module for creating and managing fields in Farmhand.
"""

from typing import Optional
from uuid import UUID

from src.api.constants import FieldTypes, FarmTypes
from src.api.core.db.models.fields import Field, PrecisionFarmingField, BaseGameField
from src.api.core.db.models.farms import Farm
from src.api.core.schema.fields import FieldRequest, PrecisionFarmingFieldModel, BaseGameFieldModel, \
    FieldResponse, FieldsResponse, FieldUpdate
from src.api.core.schema.crops.crops import CropResponse
from src.api.core.logger import logger
from src.api.services.crop_service import CropService


class FieldService:
    """
    Field Service class for field CRUD methods and any additional logic relating to fields.
    """

    def create_field_by_field_type(
        self, field_request: FieldRequest, current_farm: Farm
    ) -> FieldResponse:
        """
        Create a field based on the current farm type.
        Precision Farm's cannot create a 'Base' field and vice versa.
        :param current_farm: the id of the farm in the request
        :param field_request: the field request object.
        :return: Pydantic Model for Base Game Field, Precision Farming Field
        """
        field: Field = Field.create(
            number=field_request.number,
            size=field_request.size,
            ground_type=field_request.ground_type,
            field_type=field_request.field_type,
            plowed=field_request.plowed,
            rolled=field_request.rolled,
            mulched=field_request.mulched,
            weeds=field_request.weeds,
            farm_id=current_farm.id,
        )

        if self._is_base_game_field(field_request, current_farm):
            logger.info(
                f"Creating base game field for farm: {current_farm.name} ({current_farm.id})"
            )

            self._create_base_game_field(field.id, field_request)
            return self.get_field_details(field)

        elif self._is_precision_farming_field(field_request, current_farm):
            logger.info(
                f"Creating precision farming field for farm: {current_farm.name} ({current_farm.id})"
            )

            self._create_precision_farming_field(field.id, field_request)
            return self.get_field_details(field)

        else:
            raise ValueError(
                f"Cannot create a {field_request.field_type} on a {current_farm.farm_type} farm."
            )

    @staticmethod
    def get_field(field_id: UUID, farm_id: UUID) -> Optional[Field]:
        """
        Get the field from the database and raise an error it doesn't exist
        :param farm_id: the id of the farm that requested the field
        :param field_id: the id of the field to retrieve
        :return: the field if it exists.
        """
        field: Field = Field.get(field_id)

        # ensure that the field exists.
        if not field:
            raise ValueError("Field not found")

        # ensure that the field belongs to the farm that requested it.
        if field.farm_id != farm_id:
            raise PermissionError("You dont have access to view this field.")

        return field

    def get_all_fields(
        self, current_farm: Farm, show_crop: Optional[bool] = False, crop_type: Optional[str] = None
    ) -> dict:
        """
        Get all fields associated with a farm.
        :param current_farm: the current farm to get fields from
        :param show_crop:
        :param crop_type:
        :return: a FieldsResponse object containing all the fields and the amount.
        """
        fields = current_farm.fields
        fields, show_crop = self.filter_fields_by_crop(crop_type, fields, show_crop)

        field_details = [self.get_field_details(field, show_crop) for field in fields]
        fields_count = len(fields)
        return FieldsResponse(fields=field_details, count=fields_count).model_dump(
            exclude_none=True
        )

    def filter_fields_by_crop(
        self, crop_type: str, fields: list[Field], show_crop: bool
    ) -> tuple[list[Field], bool]:
        """
        Filter the Farm's field by matching current crop type.
        Usage: 'Get all fields growing wheat'
        :param crop_type: The crop type to get.
        :param fields: all fields to find matching crops in.
        :param show_crop: Boolean to show the crops in the response
        :return: (tuple) of fields and a 'show_crops' True.
        """
        if crop_type:
            crop = CropService.get_crop_by_type(crop_type)

            fields = self._get_fields_by_crop_id(crop.id, fields)
            # Set the show crop value to true to always return it in the response object.
            show_crop = True
        return fields, show_crop

    @staticmethod
    def _get_fields_by_crop_id(crop_id: int, fields: list[Field]) -> list[Field]:
        """
        Get fields by their crop_id
        :param crop_id: the id of the requested crop
        :param fields: all farm fields containing the same crop
        :return: a list of fields that contain the same crop.
        """
        fields = [
            field
            for field in fields
            if any(field_crop.crop_id == crop_id for field_crop in field.crops)
        ]
        return fields

    @staticmethod
    def get_field_details(field: Field, show_crops: Optional[bool] = False) -> FieldResponse:
        """
        Get the details of a field and its relationships to a base game field
        or precision farming field
        :param field: the field to get details about
        :param show_crops:
        :return: a FieldResponse object containing all the details.
        """
        field_data = FieldResponse(**field.to_dict())

        if field.field_type == FieldTypes.BASE_FIELD:
            field_data.set_base_field(BaseGameFieldModel(**field.base_game_field.to_dict()))

        if field.field_type == FieldTypes.PRECISION_FARMING_FIELD:
            field_data.set_precision_field(
                PrecisionFarmingFieldModel(**field.precision_farming_field.to_dict())
            )

        if show_crops:
            field_data.crop = CropResponse(**field.current_crop()) if field.current_crop() else None

        return field_data

    @staticmethod
    def update_field(field: Field, field_update: FieldUpdate) -> None:
        """
        Update a field and its associated field types with FieldUpdate data.
        :param field: the field to update
        :param field_update: the field update request
        """
        logger.info(
            f"Updating Field: {field.number} ({field.id}) with the following data: {field_update}"
        )
        update_data = field_update.model_dump(exclude_unset=True)
        Field.update(field.id, **update_data)

    @staticmethod
    def delete_field(field: Field) -> None:
        """
        delete a field and its associated field type by its id.
        :param field: the field to delete
        """
        logger.info(f"Deleting Field: {field.number} ({field.id})")
        Field.delete(field.id)

    @staticmethod
    def _is_base_game_field(field_request: FieldRequest, current_farm: Farm) -> bool:
        """
        Helper function to check if the request is for creating a base game field on a base game farm.
        """
        return (
            field_request.field_type == FieldTypes.BASE_FIELD
            and current_farm.farm_type == FarmTypes.BASE
        )

    @staticmethod
    def _is_precision_farming_field(field_request: FieldRequest, current_farm: Farm) -> bool:
        """
        Helper function to check if the request is creating a precision farming field
        """
        return (
            field_request.field_type == FieldTypes.PRECISION_FARMING_FIELD
            and current_farm.farm_type == FarmTypes.PRECISION_FARMING
        )

    @staticmethod
    def _create_base_game_field(field_id: UUID, field_request: FieldRequest):
        """
        Helper Function to create a Precision Farming field.
        :param field_id: the field ID to assign the base game field to.
        :param field_request: the FieldRequest object sent in the request.
        """
        BaseGameField.create(
            id=field_id, fertilized=field_request.fertilized, limed=field_request.limed
        )

    @staticmethod
    def _create_precision_farming_field(field_id: UUID, field_request: FieldRequest):
        """
        Helper Function to create a Precision Farming field.
        :param field_id: the field ID to assign the precision farming field to.
        :param field_request: the FieldRequest object sent in the request.
        """
        PrecisionFarmingField.create(
            id=field_id,
            nitrogen_level=field_request.nitrogen_level,
            ph_level=field_request.ph_level,
            soil_type=field_request.soil_type,
        )
