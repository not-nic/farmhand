"""
Unit Tests for the Field API Routes.
"""

import pytest

from typing import Optional
from uuid import UUID, uuid4
from fastapi import status
from pytest_asyncio import fixture

from src.api.constants import SoilTypes, FieldTypes
from src.api.core.db_models import Field
from src.api.core.models import FieldResponse, FieldsResponse
from src.api.services.field_service import FieldService
from tests.conftest import TestClient
from src.config import settings


@pytest.mark.usefixtures("client", "session")
class TestFieldRoutes:

    @staticmethod
    def post(url: str, json: dict, client: TestClient):
        return client.post(url, json=json)

    @staticmethod
    def put(url: str, json: dict, client: TestClient):
        return client.put(url, json=json)

    @staticmethod
    def get(url: str, client: TestClient):
        return client.get(url)

    @staticmethod
    def delete(url: str, client: TestClient):
        return client.delete(url)

    @staticmethod
    def field_url(farm_id: UUID, field_id: Optional[UUID] = None):
        field_id_path = f"/{field_id}" if field_id else ""
        return f"{settings.API_V1_STR}/farms/{farm_id}/fields{field_id_path}"

    @fixture
    def expected_base_field(self, fields):
        """
        Fixture for the expected field.
        :param fields:
        :return:
        """
        base_fields, _ = fields
        return base_fields[0]

    @fixture
    def expected_precision_field(self, fields):
        """
        Fixture for the expected field.
        :param fields:
        :return:
        """
        _, precision_farming_field = fields
        return precision_farming_field[0]

    def test_create_base_field(self, client, session, farms):
        """
        test that a base field is created and the correct field object is returned.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: farms fixture to create farms on test run
        """
        payload = {
            "number": 123,
            "field_type": "base_field",
            "ground_type": "planted",
            "size": 10.5,
            "plowed": True,
            "rolled": False,
            "mulched": True,
            "fertilized": 50,
            "weeds": 1
        }

        result = self.post(self.field_url(farm_id=farms[0].id), payload, client)

        assert result.status_code == status.HTTP_201_CREATED

        result_json = result.json()
        field_service = FieldService()
        expected_field: FieldResponse = field_service.get_field_details(Field.get(UUID(result_json["id"])))

        assert expected_field.model_dump(mode="json", exclude_none=True) == result_json

    def test_create_precision_farming_field(self, client, session, farms):
        """
        test that a precision farming field is created and the correct field object is returned.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: farms fixture to create farms on test run
        """
        payload = {
            "number": 123,
            "field_type": "precision_field",
            "ground_type": "planted",
            "size": 10.5,
            "plowed": True,
            "rolled": False,
            "mulched": True,
            "nitrogen_level": 125,
            "ph_level": 5.5,
            "soil_type": SoilTypes.LOAM
        }

        result = self.post(self.field_url(farm_id=farms[1].id), payload, client)

        assert result.status_code == status.HTTP_201_CREATED

        result_json = result.json()
        field_service = FieldService()
        expected_field: FieldResponse = field_service.get_field_details(Field.get(UUID(result_json["id"])))

        assert expected_field.model_dump(mode="json", exclude_none=True) == result_json

    def test_validation_error_when_creating_field_with_both_types(self, client, session, farms):
        """
        test that a pydantic validation error is return when a field is created with both field types.
        :param client: FastAPI Test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        """
        payload = {
            "number": 123,
            "field_type": "precision_field",
            "ground_type": "planted",
            "size": 10.5,
            "plowed": True,
            "rolled": False,
            "mulched": True,
            "fertilized": 50,
            "weeds": 1,
            "nitrogen_level": 125,
            "ph_level": 5.5,
            "soil_type": SoilTypes.LOAM
        }

        result = self.post(self.field_url(farm_id=farms[0].id), payload, client)
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        result_json = result.json()
        assert result_json["detail"][0]["msg"] == (
            "Value error, Precision Farming field values (nitrogen_level, ph_level, soil_type) cannot "
            "be used with Base Game Field specific fields (fertilized, limed)."
        )

    def test_creating_field_on_wrong_farm_type(self, client, session, farms):
        """
        test creating a base game field on a precision farming field.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        """
        payload = {
            "number": 123,
            "field_type": "base_field",
            "ground_type": "planted",
            "size": 10.5,
            "plowed": True,
            "rolled": False,
            "mulched": True,
            "fertilized": 50,
            "weeds": 1,
        }

        result = self.post(self.field_url(farm_id=farms[1].id), payload, client)
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        result_json = result.json()
        assert result_json["detail"] == "Cannot create a base_field on a precision_farming farm."

    def test_updating_field_on_base_game_farm(self, client, session, farms, expected_base_field):
        """
        Test updating a base game field on a base game farm.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param expected_base_field: the expected base field fixture
        """
        expected_farm = farms[0]

        payload = {
            "number": 999,
            "ground_type": "test-ground-type",
            "size": 15,
            "fertilized": 100,
            "weeds": 4,
        }

        result = self.put(self.field_url(farm_id=expected_farm.id, field_id=expected_base_field.id), payload, client)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_update_field_on_precision_farm(self, client, session, farms, expected_precision_field):
        """
        Test updating a precision farming field on a precision farm.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param expected_precision_field: the expected precision farming field fixture
        """
        expected_farm = farms[1]

        payload = {
            "number": 999,
            "ground_type": "test-ground-type",
            "size": 15,
            "weeds": 4,
            "nitrogen_level": 123,
            "ph_level": 9.0,
            "soil_type": SoilTypes.SILTY_CLAY
        }

        result = self.put(self.field_url(
            farm_id=expected_farm.id, field_id=expected_precision_field.id), payload, client
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_base_game_field(self, client, session, farms, expected_base_field):
        """
        Test deleting a base game field record
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param expected_base_field: the expected base field fixture
        """
        expected_farm = farms[0]

        result = self.delete(self.field_url(farm_id=expected_farm.id, field_id=expected_base_field.id), client)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_precision_farming_field(self, client, session, farms, expected_precision_field):
        """
        Test deleting a precision farming field record
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param expected_precision_field: the expected precision farming field fixture
        """
        expected_farm = farms[1]

        result = self.delete(self.field_url(farm_id=expected_farm.id, field_id=expected_precision_field.id), client)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_get_field_by_id(self, client, session, farms, fields, expected_base_field):
        """
        Test that a single farm record can be retrieved from the get endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param expected_base_field: the expected base field
        """
        expected_farm = farms[0]

        result = self.get(self.field_url(farm_id=expected_farm.id, field_id=expected_base_field.id), client)

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == expected_base_field.model_dump(mode="json")

    def test_get_field_that_does_not_exist(self, client, session, farms):
        """
        Test that a 404 error is returned when a field does not exist
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        """
        expected_farm = farms[0]

        result = self.get(
            self.field_url(farm_id=expected_farm.id, field_id=UUID("f5a22bb2-d768-4cbd-a684-4826670d452f")),
            client
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Field not found"}

    def test_get_field_for_a_different_farm(self, client, session, farms):
        """
        Test that when getting a farm for a different user it returns a 403 forbidden error.
        :param client: FastAPI test client
        :param session: the user's session
        """
        expected_farm = farms[0]

        expected_field = Field.create(
            number=123,
            size=5.0,
            ground_type="unit-test-ground-type",
            farm_id=uuid4(),
            field_type=FieldTypes.BASE_FIELD
        )

        result = self.get(
            self.field_url(farm_id=expected_farm.id, field_id=expected_field.id),
            client
        )

        assert result.status_code == status.HTTP_403_FORBIDDEN
        assert result.json() == {
            "detail": "You do not have permission to access this field; it belongs to a different farm."
        }

    def test_get_all_fields_for_a_base_game_farm(self, client, session, farms, fields):
        """
        Test that all fields for a base game farm can be retrieved and returned in the correct format.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        :param fields: fixture to create fields on test run
        """
        base_fields, _ = fields

        base_fields_results = self.get(self.field_url(farm_id=farms[0].id), client)

        assert base_fields_results.status_code == status.HTTP_200_OK
        assert base_fields_results.json()["count"] == len(base_fields)

        expected_field_json = FieldsResponse(
            fields=base_fields,
            count=len(base_fields)
        ).model_dump(mode="json", exclude_none=True)

        assert base_fields_results.json() == expected_field_json

    def test_get_all_fields_for_a_precision_farming_farm(self, client, session, farms, fields):
        """
        Test that all fields for a base game farm can be retrieved and returned in the correct format.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        :param fields: fixture to create fields on test run
        """
        precision_farming_fields: list[FieldResponse]
        _, precision_farming_fields = fields

        precision_farming_results = self.get(self.field_url(farm_id=farms[1].id), client)

        assert precision_farming_results.status_code == status.HTTP_200_OK
        assert precision_farming_results.json()["count"] == len(precision_farming_fields)

        expected_field_json = FieldsResponse(
            fields=precision_farming_fields,
            count=len(precision_farming_fields)
        ).model_dump(mode="json", exclude_none=True)

        assert precision_farming_results.json() == expected_field_json
