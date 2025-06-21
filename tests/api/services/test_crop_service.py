"""
Crop Service Unit Tests.
"""

import pytest

from src.api.core.repositories import CropRepository
from src.api.services.crop_service import CropService
from tests.utils import crop_data


@pytest.mark.asyncio
class TestCropService:
    async def test_load_crops(self, db, mock_crop_data):
        """
        Test loading the crops into the database and assert the amount in the database
        as the total crops in the drop_data.
        :param db: database fixture
        """

        crop_service = CropService(db)
        crop_repository = CropRepository(db)
        await crop_service.load_crops()
        assert len(crop_repository.all()) == len(crop_data())
