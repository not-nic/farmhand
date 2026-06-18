"""
Unit Tests for the Farm API Routes.
"""

from uuid import UUID, uuid4

import pytest
from fastapi import status

from src.api.core.repositories import FarmRepository
from src.api.exceptions.farmhand_data_api_exceptions import ServiceUnavailableError
from src.config import settings
from tests.conftest import UNIT_TESTING_USER


@pytest.mark.usefixtures("client", "session")
class TestFarmRoutes:
    url = f"{settings.API_V1_STR}/farms"

    @pytest.fixture
    def farm_repository(self, db):
        """
        Farm Repository Instance fixture.
        :param db: Database session fixture.
        :return: Farm repository instance.
        """
        return FarmRepository(db)

    def test_get_multiple_farms(self, client, session, farms):
        """
        Test that multiple created farms can be retrieved from the 'GET' endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        """

        result = client.get(self.url)

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["count"] == len(farms)

        for expected_farm, farm_data in zip(farms, result.json()["farms"], strict=True):
            assert farm_data["name"] == expected_farm.name
            assert farm_data["description"] == expected_farm.description
            assert farm_data["map_name"] == expected_farm.map_name
            assert farm_data["created_at"] is not None

    def test_get_farm(self, client, session, farms):
        """
        Test that a single farm record can be retrieved from the 'GET' endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param farms: create farms fixture
        """

        expected_farm = farms[0]

        result = client.get(f"{self.url}/{expected_farm.id}")
        result_json = result.json()

        assert result.status_code == status.HTTP_200_OK

        assert result_json["name"] == expected_farm.name
        assert result_json["description"] == expected_farm.description
        assert result_json["map_name"] == expected_farm.map_name
        assert result_json["created_at"] is not None

    def test_get_farm_that_does_not_exist(self, client, session):
        """
        Test that when requesting a farm that doesn't exist, it returns a 404.
        :param client: FastAPI test client
        :param session: the user's session
        """

        result = client.get(f"{self.url}/f5a22bb2-d768-4cbd-a684-4826670d452f")

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Farm not found."}

    def test_get_farm_for_a_different_user(self, client, session, farm_repository):
        """
        Test that when getting a farm for a different user, it returns a 403 forbidden error.
        :param client: FastAPI test client
        :param session: the user's session
        :param farm_repository: farm repository fixture.
        """
        farm = farm_repository.create(
            name="farm 1", description="description 1", map_name="map 1", owner_id=uuid4()
        )

        result = client.get(f"{self.url}/{farm.id}")

        assert result.status_code == status.HTTP_403_FORBIDDEN
        assert result.json() == {"detail": f"{UNIT_TESTING_USER} does not have access to this farm."}

    def test_create_farm_by_map_id(
            self,
            client,
            session,
            mock_map_response,
            unit_test_user,
            farm_repository
    ):
        """
        Test creating a farm by a map_id and validate it is in the database.
        :param client: FastAPI test client
        :param session: the user's session
        :param mock_map_response: fixture to create a map
        """
        payload = {
            "map_id": 123456,
        }

        result = client.post(self.url, json=payload)
        assert result.status_code == status.HTTP_201_CREATED

        result_json = result.json()
        expected_farm = farm_repository.get_by_id(UUID(result_json["id"]))

        assert expected_farm.map_name == 'custom-map-1'
        assert expected_farm.map_id == 123456
        assert expected_farm.name == 'custom-map-1 Farm'
        assert expected_farm.difficulty == "MEDIUM"
        assert expected_farm.farm_type == "base"
        assert expected_farm.description == f"{unit_test_user.username}'s new farm on custom-map-1-1.0.0.0"

    def test_create_farm_returns_404_if_no_map_is_found(self, client, session):
        """
        Test that when creating a farm with a map_id, it returns a
        404 if the map is not found.
        :param client: FastAPI test client
        :param session: the user's session
        """

        payload = {
            "map_id": 1234,
        }

        result = client.post(self.url, json=payload)
        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Map not found."}

    def test_create_farm_returns_validation_error(self, client, session):
        """
        Testing creating a farm raises a 422 error if map_id or map_name is not provided.
        :param client: FastAPI test client
        :param session: the user's session
        """

        payload = {
            "name": "test-farm",
            "description": "test-description",
        }

        result = client.post(self.url, json=payload)
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_farm(self, client, session, user_id, farm_repository):
        """
        Test updating a value in a farm record
        :param client: FastAPI test client
        :param session: the user's session
        :param user_id: the id of the unit test user
        """

        expected_farm = farm_repository.create(
            name="Old farm name",
            description="test description",
            map_name="test map",
            owner_id=user_id,
        )

        payload = {
            "name": "New farm name",
            "description": "new desc",
            "difficulty": "HARD"
        }

        result = client.patch(f"{self.url}/{expected_farm.id}", json=payload)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_farm(self, client, session, user_id, farm_repository):
        """
        Test deleting a farm record
        :param client: FastAPI test client
        :param session: the user's session
        :param user_id: the id of the unit test user
        """

        expected_farm = farm_repository.create(
            name="test name", description="test description", map_name="test map", owner_id=user_id
        )

        result = client.delete(f"{self.url}/{expected_farm.id}")
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_create_farm_returns_503_if_service_unavailable(self, client, session, mocker):
        """
        Test that when the farmhand-data-api is unavailable, it returns a 503.
        :param client: FastAPI test client
        :param session: the user's session
        :param mocker: pytest-mock fixture
        """
        mocker.patch(
            "src.api.routes.farm_routes.FarmService.create_farm",
            side_effect=ServiceUnavailableError,
        )

        payload = {"map_id": 123456}

        result = client.post(self.url, json=payload)
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert result.json() == {"detail": "Unable to communicate with farmhand-data-api."}
