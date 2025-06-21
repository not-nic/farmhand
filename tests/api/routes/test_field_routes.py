"""
Unit Tests for the Field API Routes.
"""

import pytest

from typing import Optional
from uuid import UUID, uuid4
from fastapi import status

from src.api.constants import SoilTypes, FieldTypes
from src.api.core.repositories import FieldRepository, FieldCropRepository
from src.api.core.schema.fields import FieldResponse, FieldsResponse
from src.api.services.field_service import FieldService
from src.config import settings
from tests.utils import TestClientHelper


@pytest.mark.usefixtures("client", "session", "mock_crop_data")
class TestFieldRoutes:

    @staticmethod
    def field_url(farm_id: UUID, field_number: Optional[int] = None):
        field_number_path = f"/{field_number}" if field_number else ""
        return f"{settings.API_V1_STR}/farms/{farm_id}/fields{field_number_path}"

    @pytest.fixture
    def field_repository(self, db):
        """
        Field Repository Instance fixture.
        :param db: database session fixture.
        :return: field repository instance.
        """
        return FieldRepository(db)

    def test_create_base_field(self, db, client, session, farms, field_repository):
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
            "weeds": 1,
        }

        result = TestClientHelper.post(self.field_url(farm_id=farms[0].id), payload, client)

        assert result.status_code == status.HTTP_201_CREATED

        result_json = result.json()
        field_service = FieldService(db)
        expected_field: FieldResponse = field_service.get_field_details(
            field_repository.get_by_id(UUID(result_json["id"]))
        )

        assert expected_field.model_dump(mode="json", exclude_none=True) == result_json

    def test_create_field_with_same_field_number_raises_error(self, client, session, farms, field_repository):
        """
        Test that when creating a field with the same number it raises an HTTP 400 error
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: farms fixture to create farms on test run
        """

        field_repository.create(
            number=50,
            field_type="base_field",
            ground_type="planted",
            size=10.0,
            farm_id=farms[0].id
        )

        payload = {
            "number": 50,
            "field_type": "base_field",
            "ground_type": "planted",
            "size": 10.5,
            "plowed": True,
            "rolled": False,
            "mulched": True,
            "fertilized": 50,
            "weeds": 1,
        }

        result = TestClientHelper.post(self.field_url(farm_id=farms[0].id), payload, client)

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {
            "detail": "Field 50 already exists on this farm."
        }

    def test_create_precision_farming_field(self, db, client, session, farms, field_repository):
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
            "soil_type": SoilTypes.LOAM,
        }

        result = TestClientHelper.post(self.field_url(farm_id=farms[1].id), payload, client)

        assert result.status_code == status.HTTP_201_CREATED

        result_json = result.json()
        field_service = FieldService(db)
        expected_field: FieldResponse = field_service.get_field_details(
            field_repository.get_by_id(UUID(result_json["id"]))
        )

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
            "soil_type": SoilTypes.LOAM,
        }

        result = TestClientHelper.post(self.field_url(farm_id=farms[0].id), payload, client)
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        result_json = result.json()
        assert result_json["detail"] == (
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

        result = TestClientHelper.post(self.field_url(farm_id=farms[1].id), payload, client)
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        result_json = result.json()
        assert result_json["detail"] == "Cannot create a base_field on a precision_farming farm."

    def test_updating_field_on_base_game_farm(self, client, session, farms, base_game_field):
        """
        Test updating a base game field on a base game farm.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param base_game_field: the expected base field fixture
        """

        expected_farm = farms[0]

        payload = {
            "number": 999,
            "ground_type": "test-ground-type",
            "size": 15,
            "fertilized": 100,
            "weeds": 4,
        }

        result = TestClientHelper.put(
            self.field_url(farm_id=expected_farm.id, field_number=base_game_field.number),
            payload,
            client,
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_update_field_on_precision_farm(self, client, session, farms, precision_farming_field):
        """
        Test updating a precision farming field on a precision farm.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param precision_farming_field: the expected precision farming field fixture
        """

        expected_farm = farms[1]

        payload = {
            "number": 999,
            "ground_type": "test-ground-type",
            "size": 15,
            "weeds": 4,
            "nitrogen_level": 123,
            "ph_level": 9.0,
            "soil_type": SoilTypes.SILTY_CLAY,
        }

        result = TestClientHelper.put(
            self.field_url(farm_id=expected_farm.id,  field_number=precision_farming_field.number),
            payload,
            client,
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_base_game_field(self, client, session, farms, base_game_field):
        """
        Test deleting a base game field record
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param base_game_field: the expected base field fixture
        """

        expected_farm = farms[0]

        result = TestClientHelper.delete(
            self.field_url(farm_id=expected_farm.id,  field_number=base_game_field.number), client
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_precision_farming_field(self, client, session, farms, precision_farming_field):
        """
        Test deleting a precision farming field record
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        :param precision_farming_field: the expected precision farming field fixture
        """

        expected_farm = farms[1]

        result = TestClientHelper.delete(
            self.field_url(farm_id=expected_farm.id,  field_number=precision_farming_field.number), client
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_get_field_by_number(self, db, client, session, farms, base_game_field):
        """
        Test that a single farm record can be retrieved from the get endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        """

        expected_farm = farms[0]

        result = TestClientHelper.get(
            self.field_url(farm_id=expected_farm.id,  field_number=base_game_field.number), client
        )

        field_service = FieldService(db)
        expected_field = field_service.get_field_details(base_game_field)

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == expected_field.model_dump(mode="json", exclude_none=True)

    def test_get_field_that_does_not_exist(self, client, session, farms):
        """
        Test that a 404 error is returned when a field does not exist
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        """

        expected_farm = farms[0]

        result = TestClientHelper.get(self.field_url(farm_id=expected_farm.id,  field_number=66), client)

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Field not found."}

    def test_get_field_for_a_different_farm(self, client, session, farms, field_repository):
        """
        Test that when getting a farm for a different user it returns a 403 forbidden error.
        :param client: FastAPI test client
        :param session: the user's session
        """

        expected_farm = farms[0]

        expected_field = field_repository.create(
            number=123,
            size=5.0,
            ground_type="unit-test-ground-type",
            farm_id=uuid4(),
            field_type=FieldTypes.BASE_FIELD,
        )

        result = TestClientHelper.get(
            self.field_url(farm_id=expected_farm.id, field_number=expected_field.number), client
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {
            "detail": "Field not found."
        }

    def test_get_all_fields_for_a_base_game_farm(self, client, session, farms, base_game_fields):
        """
        Test that all fields for a base game farm can be retrieved and returned in the correct format.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        :param base_game_fields: fixture of base game fields
        """

        base_fields_results = TestClientHelper.get(self.field_url(farm_id=farms[0].id), client)

        assert base_fields_results.status_code == status.HTTP_200_OK
        assert base_fields_results.json()["count"] == len(base_game_fields)

        expected_field_json = FieldsResponse(fields=base_game_fields, count=len(base_game_fields)).model_dump(
            mode="json", exclude_none=True
        )

        assert base_fields_results.json() == expected_field_json

    def test_get_all_fields_for_a_precision_farming_farm(self, client, session, farms, precision_farming_fields):
        """
        Test that all fields for a base game farm can be retrieved and returned in the correct format.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        :param precision_farming_fields: fixture of precision farming fields
        """

        precision_farming_results = TestClientHelper.get(self.field_url(farm_id=farms[1].id), client)

        assert precision_farming_results.status_code == status.HTTP_200_OK
        assert precision_farming_results.json()["count"] == len(precision_farming_fields)

        expected_field_json = FieldsResponse(
            fields=precision_farming_fields, count=len(precision_farming_fields)
        ).model_dump(mode="json", exclude_none=True)

        assert precision_farming_results.json() == expected_field_json

    def test_getting_fields_with_the_current_crop(
            self,
            client,
            session,
            farms,
            base_game_field,
            db
    ):
        """
        test getting a field with the query 'show_crops' true and assert that a crop
        object exists in the response.
        :param client: FastAPI Test Client
        :param session: Unit test session
        :param farms: farms fixture
        :param base_game_field: base field fixture
        :param db: database session fixture
        """
        field_crop_repository = FieldCropRepository(db)
        field_crop_repository.create(field_id=base_game_field.id, crop_id=1)

        url = (
            f"{self.field_url(farm_id=farms[0].id, field_number=base_game_field.number)}?show_crop=true"
        )
        response = TestClientHelper.get(url=url, client=client)

        assert response.status_code == status.HTTP_200_OK
        assert "crop" in response.json()

    def test_getting_fields_that_have_the_same_crop(
            self,
            client,
            session,
            farms,
            base_game_fields,
            db
    ):
        """
        test getting a field with the query 'show_crops' true and assert that a crop
        object exists in the response and a 200 response code is asserted.
        :param client: FastAPI Test Client
        :param session: unit test session fixture
        :param farms: farms fixture
        :param base_game_fields: base game fields fixture
        :param db: database session fixture
        :return:
        """
        field_crop_repository = FieldCropRepository(db)
        field_crop_repository.create(field_id=base_game_fields[0].id, crop_id=1)
        field_crop_repository.create(field_id=base_game_fields[1].id, crop_id=1)
        field_crop_repository.create(field_id=base_game_fields[2].id, crop_id=1)

        url = f"{self.field_url(farm_id=farms[0].id)}?crop_type=Wheat"
        response = TestClientHelper.get(url=url, client=client)

        assert response.status_code == status.HTTP_200_OK

        for field in response.json()["fields"]:
            assert field["crop"]["crop_type"] == "Wheat"

    def test_getting_fields_with_an_invalid_crop(self, client, session, farms):
        """
        test getting fields with an invalid crop type and assert a 400 error is
        raised.
        :param client: FastAPI Test Client
        :param session: Unit test session
        :param farms: farms fixture
        """

        invalid_crop = "Invalid-Crop-Type"
        url = f"{self.field_url(farm_id=farms[0].id)}?crop_type={invalid_crop}"
        response = TestClientHelper.get(url=url, client=client)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": f"Invalid crop: '{invalid_crop}' not found"}
