"""
Crop Service Module for interacting and managing with crops that are associated with fields
"""

import json
import os.path

from typing import Optional

from src.api.constants import FSData
from src.api.core.schema.crops import CropModel, CropRequest, CropResponse
from src.api.core.db.models.fields import FieldCrop, Field
from src.api.core.db.models.crops import Crop
from src.api.core.logger import logger


class CropService:
    """
    Crop Service:

    This service is responsible for managing crops on a user's farm, including adding, updating,
    and retrieving crop data.
    It also handles the initialization of crops during the application's startup.
    """

    def plant_crop(self, current_field: Field, crop_request: CropRequest) -> FieldCrop:
        """
        Plant (create) a crop and assign it to a field.
        :param current_field: The current field to create a crop on.
        :param crop_request: the crop request object.
        :return: the new created field crop.
        """
        crop = self.get_crop_by_type(crop_request.crop_type)
        Field.update(id=current_field.id, ground_type=crop_request.ground_type)
        return FieldCrop.create(crop_id=crop.id, field_id=current_field.id)

    def get_past_crops(self, current_field: Field) -> list[CropResponse]:
        """
        Get the 'past' crops that have been planted on a field.
        :param current_field: the current field to get crops for.
        :return: a list of the past crops
        """
        return self.format_crop_response(current_field.past_crops())

    def get_current_crop(self, current_field: Field) -> list[CropResponse]:
        """
        Get the current crops that have been planted on a field.
        :param current_field: the current field to get crops for.
        :return: a list of the current crop.
        """
        return self.format_crop_response([current_field.current_crop()])

    def get_all_crops(self, current_field: Field) -> list[CropResponse]:
        """
        Get all the crops that have been planted in a field.
        :param current_field: the current field to get data for.
        :return: a list of all the crops that have been planted on a field.
        """
        return self.format_crop_response(current_field.get_crops())

    @staticmethod
    def estimate_seed_usage(current_field: Field) -> float:
        """

        :param current_field:
        :return:
        """
        crop: Crop = Crop.get(current_field.current_crop().crop_id)
        return current_field.size * crop.seeds_per_ha

    @staticmethod
    def estimate_seed_costs(seed_usage: float) -> float:
        """
        Estimate the seed costs for a field by multiplying the seed usage
        by the seed price (£1.26).
        :param seed_usage: estimated seed usage in a particular feed.
        :return: (float) the cost to seed a field.
        """

        return seed_usage * FSData.BASE_SEED_PRICE.value

    @staticmethod
    def get_crop_by_type(crop_type: str) -> Optional[Crop]:
        """
        Get a crop by its crop_type e.g. wheat, barley etc.
        :param crop_type: the crop type to get
        :return: the crop if it exists.
        """
        crop = Crop.get_by_type(crop_type)

        if not crop:
            raise ValueError(f"Invalid crop: '{crop_type}' not found")
        return crop

    @staticmethod
    def format_crop_response(field_crops: list[FieldCrop]) -> list[CropResponse]:
        """
        Helper function to format crop response.
        :param field_crops: List of crops
        :return: CropsResponse pydantic model containing the field crops and the count.
        """
        return [
            CropResponse(id=field_crop.id, crop_type=field_crop.crop.type, planted_at=field_crop.planted_at)
            for field_crop in field_crops
        ]

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

            existing_crop = Crop.get_by_type(type=crop_data.type)

            if existing_crop:
                existing_crop.update(existing_crop.id, **crop_dict)
            else:
                logger.info(f"[Crop Service]: Creating new crop '{crop_data.type}'")
                Crop.create(**crop_dict)

        logger.info(
            "[Crop Service]: All Crops created, updated values successfully if any changed."
        )

    @staticmethod
    def _load_crop_data_from_fixture() -> dict:
        """
        util function to load the crop data from the fixture
        crop_data.json.
        :return: the default JSON crop data
        """
        filepath = os.path.join("src", "api", "fixtures", "resources", "crop_data.json")
        logger.info(f"[Crop Service]: Loading crop data from path: {filepath}")
        with open(filepath, "r") as file:
            return json.load(file)
