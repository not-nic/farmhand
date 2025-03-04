from fastapi import status
from fastapi.testclient import TestClient


class TestAuthRoutes:
    url = "api/v1/login"

    @staticmethod
    def post(url: str, data: dict, client: TestClient):
        return client.post(url, json=data)

    def test_login_without_credentials(self, client):
        payload = {
            "username": "notauser",
            "password": "notapassword"
        }

        response = self.post(url=self.url, data=payload, client=client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials"}

    def test_login_with_credentials(self, client, create_test_user):
        payload = {
            "username": "unit-testing-user",
            "password": "unit-testing-password"
        }

        response = self.post(url=self.url, data=payload, client=client)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.cookies.get("session")) == 128
        assert response.json() == {"message": "login successful"}