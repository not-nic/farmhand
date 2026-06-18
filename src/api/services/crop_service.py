"""
Crop Service Module for interacting and managing with crops that are associated with fields
"""

import json
import os.path

from sqlalchemy.orm import Session

from src.api.core.db.models.crops import Crop
from src.api.core.db.models.fields import Field, FieldCrop
from src.api.core.logger import logger
from src.api.core.repositories import CropRepository, FieldCropRepository, FieldRepository
from src.api.core.schema.crops import CropModel, CropRequest, CropResponse


class CropService:
    """
    Crop Service:

    This service is responsible for managing crops on a user's farm, including adding, updating,
    and retrieving crop data.
    It also handles the initialisation of crops during the application's startup.
    """

    def __init__(self, db: Session):
        self.field_repository = FieldRepository(db)
        self.crop_repository = CropRepository(db)
        self.field_crop_repository = FieldCropRepository(db)

    async def plant_crop(self, current_field: Field, crop_request: CropRequest) -> FieldCrop:
        """
        Plant (create) a crop and assign it to a field.
        :param current_field: The current field to create a crop on.
        :param crop_request: the crop request object.
        :return: the new created field crop.
        """
        crop = await self.get_crop_by_type(crop_request.crop_type)

        if not crop_request.ground_type:
            self.field_repository.update(current_field, ground_type=crop_request.ground_type)

        logger.info(f"[Crop Service]: Planting '{crop.type}' in field: '{current_field.id}'")
        return self.field_crop_repository.create(crop_id=crop.id, field_id=current_field.id)

    async def get_past_crops(self, current_field: Field) -> list[CropResponse]:
        """
        Get the 'past' crops that have been planted on a field.
        :param current_field: the current field to get crops for.
        :return: a list of the past crops
        """
        return self.format_crop_response(current_field.past_crops())

    async def get_current_crop(self, current_field: Field) -> list[CropResponse]:
        """
        Get the current crops that have been planted on a field.
        :param current_field: the current field to get crops for.
        :return: a list of the current crop.
        """
        return self.format_crop_response([current_field.current_crop()])

    async def get_all_crops(self, current_field: Field) -> list[CropResponse]:
        """
        Get all the crops that have been planted in a field.
        :param current_field: the current field to get data for.
        :return: a list of all the crops that have been planted on a field.
        """
        return self.format_crop_response(current_field.get_crops())

    async def load_crops(self, crop_data: dict = None) -> None:
        """
        Load crop information into the database on application start up or
        overwrite it with different crop data later.
        :param crop_data: crop data such as yield, growth_duration etc.
        """
        crop_data = crop_data or self._load_crop_data_from_fixture()

        for crop in crop_data:
            crop_data = CropModel(**crop)
            crop_dict = crop_data.model_dump()

            existing_crop = self.crop_repository.get_by_type(type=crop_data.type)

            if existing_crop:
                self.crop_repository.update(existing_crop, **crop_dict)
            else:
                logger.info(f"[Crop Service]: Creating new crop '{crop_data.type}'")
                self.crop_repository.create(**crop_dict)

        logger.info(
            "[Crop Service]: All Crops created, updated values successfully if any changed."
        )

    async def get_crop_by_type(self, crop_type: str) -> Crop | None:
        """
        Get a crop by its crop_type e.g. wheat, barley, etc.
        :param crop_type: the crop type to get
        :return: the crop if it exists.
        """
        crop = self.crop_repository.get_by_type(type=crop_type)

        if not crop:
            logger.info(f"[Crop Service]: Invalid crop: '{crop_type}' not found")
            raise ValueError(f"Invalid crop: '{crop_type}' not found")
        return crop

    async def get_crop_details(self, crop_id: int) -> Crop | None:
        """
        Get all the details for a 'Crop' i.e.
        :param crop_id: the id of the crop to get
        :return:
        """
        crop = self.crop_repository.get_by_id(crop_id)

        if not crop:
            logger.info(f"[Crop Service]: Invalid crop: '{crop_id}' not found")
            raise ValueError(f"Invalid crop: '{crop_id}' not found")
        return crop

    @staticmethod
    def format_crop_response(field_crops: list[FieldCrop]) -> list[CropResponse]:
        """
        Helper function to format crop response.
        :param field_crops: List of crops
        :return: CropsResponse pydantic model containing the field crops and the count.
        """
        return [
            CropResponse(
                id=field_crop.id, crop_type=field_crop.crop.type, planted_at=field_crop.planted_at
            )
            for field_crop in field_crops
        ]

    @staticmethod
    def _load_crop_data_from_fixture() -> dict:
        """
        util function to load the crop data from the fixture
        crop_data.json.
        :return: the default JSON crop data
        """
        filepath = os.path.join("src", "api", "fixtures", "resources", "crop_data.json")
        logger.info(f"[Crop Service]: Loading crop data from path: {filepath}")
        with open(filepath) as file:
            return json.load(file)
