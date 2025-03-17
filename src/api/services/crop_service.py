import json
import os.path

from src.api.core.models import CropModel
from src.api.core.db_models import Crop
from src.api.utils import logger


class CropService:
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

        logger.info("[Crop Service]: All Crops created, updated values successfully if any changed.")

    @staticmethod
    def _load_crop_data_from_fixture() -> dict:
        """
        util function to load the crop data from the fixture
        crop_data.json.
        :return: the default JSON crop data
        """
        filepath = os.path.join("src", "api", "fixtures", "resources", "crop_data.json")
        logger.info(f"[Crop Service]: Getting crop information from file at path: {filepath}")
        with open(filepath, "r") as file:
            return json.load(file)
