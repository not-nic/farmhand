from typing import Optional, List, Union
from uuid import UUID
from fastapi import status

from src.api.constants import FertilizerStates, WeedStates, SoilTypes
from src.api.core.db_models import Field
from src.api.core.models import BaseGameFieldModel, PrecisionFarmingFieldModel
from tests.conftest import TestClient
from src.config import settings


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
        expected_field: dict = Field.get(UUID(result_json["id"])).get_field_details()

        for key, value in payload.items():
            if key == "fertilized":
                expected_enum_value = FertilizerStates(value)
                assert expected_field.get(key) == expected_enum_value
            elif key == "weeds":
                expected_enum_value = WeedStates(value)
                assert expected_field.get(key) == expected_enum_value
            else:
                assert expected_field.get(key) == value

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
        expected_field: dict = Field.get(UUID(result_json["id"])).get_field_details()

        for key, value in payload.items():
            assert expected_field.get(key) == value

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

    def test_get_field_by_id(self, client, session, farms, fields):
        """
        Test that a single farm record can be retrieved from the get endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        """
        expected_farm = farms[0]

        base_fields: List[BaseGameFieldModel]
        base_fields, _ = fields
        expected_field = base_fields[0]

        result = self.get(self.field_url(farm_id=expected_farm.id, field_id=expected_field.id), client)
        result_json = result.json()

        assert result.status_code == status.HTTP_200_OK

        self.assert_field_info_matches(expected_field, result_json)

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

    def test_get_all_fields_for_a_base_game_farm(self, client, session, farms, fields):
        """
        Test that all fields for a base game farm can be retrieved and returned in the correct format.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        :param fields: fixture to create fields on test run
        """
        base_fields: List[BaseGameFieldModel]
        base_fields, _ = fields

        base_fields_results = self.get(self.field_url(farm_id=farms[0].id), client)

        assert base_fields_results.status_code == status.HTTP_200_OK
        assert base_fields_results.json()["count"] == len(base_fields)

        self.assert_fields_equal(base_fields, base_fields_results.json()["fields"])

    def test_get_all_fields_for_a_precision_farming_farm(self, client, session, farms, fields):
        """
        Test that all fields for a base game farm can be retrieved and returned in the correct format.
        :param client: FastAPI test client
        :param session: Current user session
        :param farms: fixture to create farms on test run
        :param fields: fixture to create fields on test run
        """
        precision_farming_fields: List[PrecisionFarmingFieldModel]
        _, precision_farming_fields = fields

        precision_farming_results = self.get(self.field_url(farm_id=farms[1].id), client)

        assert precision_farming_results.status_code == status.HTTP_200_OK
        assert precision_farming_results.json()["count"] == len(precision_farming_fields)

        self.assert_fields_equal(precision_farming_fields, precision_farming_results.json()["fields"])

    def assert_fields_equal(
            self,
            expected_fields: Union[List[BaseGameFieldModel], List[PrecisionFarmingFieldModel]],
            field_data_list: list[dict]
    ) -> None:
        """
        Util function to assert that each field in the response matches the expected values.
        :param expected_fields: List of expected fields (BaseField or PrecisionFarmingField)
        :param field_data_list: List of field data from the API response
        """
        for expected_field, field_data in zip(expected_fields, field_data_list):
            self.assert_field_info_matches(expected_field, field_data)

    @staticmethod
    def assert_field_info_matches(
            expected_field: Union[BaseGameFieldModel, PrecisionFarmingFieldModel],
            field_data: dict
    ) -> None:
        """
        Helper function to compare a single field's data.
        :param expected_field: The expected field (BaseField or PrecisionFarmingField)
        :param field_data: The field data from the API response
        """
        assert field_data["number"] == expected_field.number
        assert field_data["ground_type"] == expected_field.ground_type
        assert field_data["size"] == expected_field.size
        assert field_data["plowed"] == expected_field.plowed
        assert field_data["rolled"] == expected_field.rolled
        assert field_data["mulched"] == expected_field.mulched
        assert field_data["created_at"] is not None

        # Add specific checks for precision farming fields
        if hasattr(expected_field, 'nitrogen_level'):
            assert field_data["nitrogen_level"] == expected_field.nitrogen_level
        if hasattr(expected_field, 'ph_level'):
            assert field_data["ph_level"] == expected_field.ph_level
        if hasattr(expected_field, 'soil_type'):
            assert field_data["soil_type"] == expected_field.soil_type
        if hasattr(expected_field, 'fertilized'):
            assert FertilizerStates(field_data["fertilized"]) == expected_field.fertilized
        if hasattr(expected_field, 'limed'):
            assert field_data["limed"] == expected_field.limed