import pytest

from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from fastapi import status

from src.api.core.db_models import User, Farm
from src.config import settings
from tests.conftest import UNIT_TESTING_USER


class TestFarmRoutes:
    url = f"{settings.API_V1_STR}/farm"

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

    @pytest.fixture
    def create_farms(self, user_id) -> list[Farm]:
        farms = [
            Farm.create(name="farm 1", description="description 1", map="map 1", owner_id=user_id),
            Farm.create(name="farm 2", description="description 2", map="map 3", owner_id=user_id),
            Farm.create(name="farm 3", description="description 3", map="map 3", owner_id=user_id),
        ]
        return farms

    @pytest.fixture
    def user_id(self) -> UUID:
        return User.get_by_username(UNIT_TESTING_USER).id

    def test_get_multiple_farms(self, client, session, create_farms):
        """
        Test that multiple created farms can be retrieved from the get endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param create_farms: create farms fixture
        """
        result = self.get(self.url, client)

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["count"] == len(create_farms)

        for expected_farm, farm_data in zip(create_farms, result.json()["farms"]):
            assert farm_data["name"] == expected_farm.name
            assert farm_data["description"] == expected_farm.description
            assert farm_data["map"] == expected_farm.map
            assert farm_data["created_at"] is not None

    def test_get_farm(self, client, session, create_farms):
        """
        Test that a single farm record can be retrieved from the get endpoint.
        :param client: FastAPI test client
        :param session: the user's session
        :param create_farms: create farms fixture
        """
        expected_farm = create_farms[0]

        result = self.get(f"{self.url}/{expected_farm.id}", client)
        result_json = result.json()

        assert result.status_code == status.HTTP_200_OK

        assert result_json["name"] == expected_farm.name
        assert result_json["description"] == expected_farm.description
        assert result_json["map"] == expected_farm.map
        assert result_json["created_at"] is not None

    def test_get_farm_that_does_not_exist(self, client, session):
        """
        Test that when requesting a farm that doesn't exist it returns a 404.
        :param client: FastAPI test client
        :param session: the user's session
        """
        result = self.get(f"{self.url}/f5a22bb2-d768-4cbd-a684-4826670d452f", client)

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Farm not found"}

    def test_get_farm_for_a_different_user(self, client, session):
        """
        Test that when getting a farm for a different user it returns a 403 forbidden error.
        :param client: FastAPI test client
        :param session: the user's session
        """
        farm = Farm.create(
            name="farm 1", description="description 1", map="map 1", owner_id=uuid4()
        )

        result = self.get(f"{self.url}/{farm.id}", client)

        assert result.status_code == status.HTTP_403_FORBIDDEN
        assert result.json() == {"detail": f"{UNIT_TESTING_USER} does not own this farm."}

    def test_create_farm(self, client, session):
        """
        Test creating a farm and validate it is in the database.
        :param client: FastAPI test client
        :param session: the user's session
        """
        payload = {
            "name": "test-farm",
            "description": "test-description",
            "map": "test-map",
        }

        result = self.post(self.url, payload, client)

        assert result.status_code == status.HTTP_201_CREATED

        result_json = result.json()
        expected_farm = Farm.get(UUID(result_json["id"])).to_dict()

        for key, value in payload.items():
            assert expected_farm.get(key) == value

    def test_update_farm(self, client, session, user_id):
        """
        Test updating a value in a farm record
        :param client: FastAPI test client
        :param session: the user's session
        :param user_id: the id of the unit test user
        """
        expected_farm = Farm.create(
            name="Old farm name", description="test description", map="test map", owner_id=user_id
        )

        payload = {"name": "New farm name"}

        result = self.put(f"{self.url}/{expected_farm.id}", payload, client)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_farm(self, client, session, user_id):
        """
        Test deleting a farm record
        :param client: FastAPI test client
        :param session: the user's session
        :param user_id: the id of the unit test user
        """
        expected_farm = Farm.create(
            name="test name", description="test description", map="test map", owner_id=user_id
        )

        result = self.delete(f"{self.url}/{expected_farm.id}", client)
        assert result.status_code == status.HTTP_204_NO_CONTENT
