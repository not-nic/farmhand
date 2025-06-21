"""
Unit Tests for the Crops API Routes.
"""

import pytest

from typing import Optional
from uuid import UUID
from fastapi import status

from src.api.core.db.models.fields import FieldCrop
from src.api.core.repositories import FieldCropRepository
from src.api.core.schema.crops.crops import CropsResponse
from src.api.services.crop_service import CropService
from src.config import settings
from tests.utils import TestClientHelper


@pytest.mark.asyncio
@pytest.mark.usefixtures("client", "session", "mock_crop_data")
class TestCropRoutes:
    """
    Class for unit testing the Crops API PUT & GET Methods.
    """

    @pytest.fixture
    def field_crop_repository(self, db):
        """
        Field Crop Repository fixture
        :param db: database session fixture
        :return: FieldCropRepository instance
        """
        return FieldCropRepository(db)

    @staticmethod
    def crop_url(farm_id: UUID, field_number: Optional[int] = None):
        return f"{settings.API_V1_STR}/farms/{farm_id}/fields/{field_number}/crops"

    async def test_get_field_crops(
        self, client, session, farm, base_game_field, field_crop_repository, db
    ):
        """
        Test that when a GET request is made for a fields crops all are returned
        and match the specified json output.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param base_game_field: base game field fixture
        """

        field_crop_repository.create(field_id=base_game_field.id, crop_id=1)

        response = TestClientHelper.get(
            self.crop_url(farm_id=farm.id, field_number=base_game_field.number), client
        )
        crop_service = CropService(db)
        expected_crops = await crop_service.get_all_crops(base_game_field)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(
            crops=expected_crops, count=len(expected_crops)
        ).model_dump(mode="json")

    def test_get_field_with_no_crops(self, client, session, farm, base_game_field):
        """
        Test that when a GET request is made for a field with no crops an empty
        list is returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param base_game_field: base game field fixture
        """

        response = TestClientHelper.get(
            self.crop_url(farm_id=farm.id, field_number=base_game_field.number), client
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(crops=[], count=0).model_dump(mode="json")

    async def test_getting_the_current_field_crop(
        self, client, session, farm, base_game_field, field_crop_repository, db
    ):
        """
        Test that when a GET request is made with the query '?current=true' only
        the current field crop is returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param base_game_field: base game field fixture
        """

        field_crop_repository.create(field_id=base_game_field.id, crop_id=1)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=5)

        url = f"{self.crop_url(farm_id=farm.id, field_number=base_game_field.number)}/?current=true"

        response = TestClientHelper.get(url, client)
        crop_service = CropService(db)
        expected_crops = await crop_service.get_current_crop(base_game_field)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(
            crops=expected_crops, count=len(expected_crops)
        ).model_dump(mode="json")

    async def test_getting_the_past_field_crops(
        self, client, session, farm, base_game_field, field_crop_repository, db
    ):
        """
        Test that when a GET request is made with the query '?past=true' only
        the past field crops are returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param base_game_field: base game field fixture
        """

        field_crop_repository.create(field_id=base_game_field.id, crop_id=1)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=5)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=2)

        url = f"{self.crop_url(farm_id=farm.id, field_number=base_game_field.number)}/?past=true"

        response = TestClientHelper.get(url, client)
        crop_service = CropService(db)
        expected_crops = await crop_service.get_past_crops(base_game_field)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(
            crops=expected_crops, count=len(expected_crops)
        ).model_dump(mode="json")

    async def test_planting_crop_in_field(self, client, session, farm, base_game_field):
        """
        Test that a crop can be planted (created) and linked to a field and
        asser the current crop is the one in the payload.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param base_game_field: base game field fixture
        """

        payload = {"type": "Canola"}

        response = TestClientHelper.put(
            self.crop_url(farm_id=farm.id, field_number=base_game_field.number),
            json=payload,
            client=client,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        f_crop: FieldCrop = base_game_field.current_crop()

        assert f_crop.crop.type == "Canola"

    async def test_planting_crop_that_does_not_exist(self, client, session, farm, base_game_field):
        """
        Test that when planting a crop that doesn't exist a 400 bad request error is returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param base_game_field: base game field fixture
        """

        payload = {"type": "invalid-crop-type"}

        response = TestClientHelper.put(
            self.crop_url(farm_id=farm.id, field_number=base_game_field.number),
            json=payload,
            client=client,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": f"Invalid crop: '{payload['type']}' not found"}
