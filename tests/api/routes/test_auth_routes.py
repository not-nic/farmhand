"""
Unit Tests for the Auth API Routes.
"""

import pytest

from fastapi import status
from src.config import settings
from tests.utils import TestClientHelper


class TestAuthRoutes:
    url = f"{settings.API_V1_STR}/auth"

    def test_login_without_credentials(self, client):
        """
        Test logging into the Farmhand service with a username and password
        with incorrect credentials and assert a 401 error is returned.
        :param client: FastAPI client
        """

        payload = {"username": "notauser", "password": "notapassword"}

        response = TestClientHelper.post(url=f"{self.url}/login", client=client, json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Username or password is incorrect"}

    def test_login_with_credentials(self, client, unit_test_user):
        """
        Test logging into the Farmhand service with a username and password
        with the correct credentials and asset a 200 success.
        :param client: FastAPI client
        :param unit_test_user: the unit test user fixture
        """

        payload = {"username": "unit-testing-user", "password": "unit-testing-password"}

        response = TestClientHelper.post(url=f"{self.url}/login", json=payload, client=client)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "login successful"}

    @pytest.mark.asyncio
    async def test_login_with_github(self, client, mock_github_login, github_user):
        """
        test logging in with GitHub authentication
        :param client: FastAPI test client
        :param github_user: GitHub user fixture
        """

        response = TestClientHelper.get(f"{self.url}/github", client)
        mock_github_login.assert_called_once()
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    @pytest.mark.asyncio
    async def test_github_callback_existing_user(
        self, client, mock_github_authentication, github_user
    ):
        """
        Test github callback and mock logging in a github user.
        :param client: FastAPI test client
        :param client: FastAPI test client
        :param github_user: GitHub user fixture
        """

        response = TestClientHelper.get(f"{self.url}/github/callback", client)
        assert response.status_code == status.HTTP_200_OK

    def test_logout_of_service(self, client, session):
        """
        Test logging out of the service and assert a 204 is returned.
        :param client: FastAPI client
        """

        # Log out of the service, and delete the JWT token.
        response = TestClientHelper.post(url=f"{self.url}/logout", json={}, client=client)
        assert response.status_code == status.HTTP_204_NO_CONTENT
