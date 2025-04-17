"""
Unit Tests for the Crops API Routes.
"""

import pytest

from typing import Optional
from uuid import UUID
from fastapi import status

from src.api.core.db.models.fields import Field, FieldCrop
from src.api.core.db.models.farms import Farm
from src.api.core.schema.crops.crops import CropsResponse
from src.api.services.crop_service import CropService
from src.config import settings
from tests.utils import TestClientHelper


@pytest.mark.asyncio
@pytest.mark.usefixtures("client", "session")
class TestCropRoutes:
    """
    Class for unit testing the Crops API PUT & GET Methods.
    """

    @staticmethod
    def crop_url(farm_id: UUID, field_number: Optional[int] = None):
        return f"{settings.API_V1_STR}/farms/{farm_id}/fields/{field_number}/crops"

    @pytest.fixture
    def farm(self, farms):
        """
        Single farm fixture
        :param farms: farms fixture.
        """
        return farms[0]

    @pytest.fixture
    def field(self, fields):
        """
        Single field fixture
        :param fields: fields fixture.
        """
        base_fields, _ = fields
        return Field.get(base_fields[0].id)

    async def test_get_field_crops(self, client, session, farm, field):
        """
        Test that when a GET request is made for a fields crops all are returned
        and match the specified json output.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param field: a field fixture
        """
        FieldCrop.create(field_id=field.id, crop_id=1)

        response = TestClientHelper.get(self.crop_url(farm_id=farm.id, field_number=field.number), client)
        crop_service = CropService()
        expected_crops = await crop_service.get_all_crops(field)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(
            crops=expected_crops, count=len(expected_crops)
        ).model_dump(mode="json")

    def test_get_field_with_no_crops(self, client, session, farm, field):
        """
        Test that when a GET request is made for a field with no crops an empty
        list is returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param field: a field fixture
        """
        response = TestClientHelper.get(self.crop_url(farm_id=farm.id, field_number=field.number), client)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(crops=[], count=0).model_dump(mode="json")

    async def test_getting_the_current_field_crop(self, client, session, farm, field):
        """
        Test that when a GET request is made with the query '?current=true' only
        the current field crop is returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param field: a field fixture
        """
        FieldCrop.create(field_id=field.id, crop_id=1)
        FieldCrop.create(field_id=field.id, crop_id=5)

        url = f"{self.crop_url(farm_id=farm.id, field_number=field.number)}/?current=true"

        response = TestClientHelper.get(url, client)
        crop_service = CropService()
        expected_crops = await crop_service.get_current_crop(field)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(
            crops=expected_crops, count=len(expected_crops)
        ).model_dump(mode="json")

    async def test_getting_the_past_field_crops(self, client, session, farm, field):
        """
        Test that when a GET request is made with the query '?past=true' only
        the past field crops are returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        :param field: a field fixture
        """
        FieldCrop.create(field_id=field.id, crop_id=1)
        FieldCrop.create(field_id=field.id, crop_id=5)
        FieldCrop.create(field_id=field.id, crop_id=2)

        url = f"{self.crop_url(farm_id=farm.id, field_number=field.number)}/?past=true"

        response = TestClientHelper.get(url, client)
        crop_service = CropService()
        expected_crops = await crop_service.get_past_crops(field)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == CropsResponse(
            crops=expected_crops, count=len(expected_crops)
        ).model_dump(mode="json")

    async def test_planting_crop_in_field(self, client, session, farm: Farm, field: Field):
        """
        Test that a crop can be planted (created) and linked to a field and
        asser the current crop is the one in the payload.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        """
        payload = {"type": "Canola"}

        response = TestClientHelper.put(
            self.crop_url(farm_id=farm.id, field_number=field.number), json=payload, client=client
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert field.current_crop().crop.type == "Canola"

    async def test_planting_crop_that_does_not_exist(self, client, session, farm: Farm, field: Field):
        """
        Test that when planting a crop that doesn't exist a 400 bad request error is returned.
        :param client: FastAPI Test Client
        :param session: The unit-test user session
        :param farm: a farm fixture
        """
        payload = {"type": "invalid-crop-type"}

        response = TestClientHelper.put(
            self.crop_url(farm_id=farm.id, field_number=field.number), json=payload, client=client
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": f"Invalid crop: '{payload['type']}' not found"}
