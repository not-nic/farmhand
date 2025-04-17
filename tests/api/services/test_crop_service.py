"""
Crop Service Unit Tests.
"""

import pytest

from src.api.core.db.models.crops import Crop
from src.api.services.crop_service import CropService
from tests.utils import crop_data


@pytest.mark.asyncio
class TestCropService:
    async def test_load_crops(self, create_database, mock_crop_data):
        """
        Test loading the crops into the database and assert the amount in the database
        as the total crops in the drop_data.
        :param create_database: create database fixture
        """

        crop_service = CropService()
        await crop_service.load_crops()
        assert len(Crop.all()) == len(crop_data())
