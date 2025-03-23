from fastapi import status
from fastapi.testclient import TestClient
from src.config import settings


class TestAuthRoutes:
    url = f"{settings.API_V1_STR}/auth/login"

    @staticmethod
    def post(url: str, data: dict, client: TestClient):
        return client.post(url, json=data)

    def test_login_without_credentials(self, client):
        payload = {"username": "notauser", "password": "notapassword"}

        response = self.post(url=self.url, data=payload, client=client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Username or password is incorrect"}

    def test_login_with_credentials(self, client, create_test_user):
        payload = {"username": "unit-testing-user", "password": "unit-testing-password"}

        response = self.post(url=self.url, data=payload, client=client)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "login successful"}
