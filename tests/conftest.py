"""
Pytest conftest.py containing test setup, TestClient Fixtures and other mocks.
"""

from typing import Optional, Any, Generator

import pytest

from dotenv import load_dotenv
from fastapi import status
from fastapi.testclient import TestClient
from requests import Response

from tests.utils import load_test_resource, crop_data

load_dotenv("tests/resources/test.env", override=True)

# ruff: noqa: E402
from main import app
from main import settings
from src.api.core.db.db_setup import engine, SessionLocal
from src.api.core.repositories import UserRepository
from src.api.core.db.models import User
from src.api.core.db.models._model_base import SqlAlchemyBase
from src.api.core.security import Security, github
from src.api.services.crop_service import CropService

pytest_plugins = "tests.fixtures"


UNIT_TESTING_USER = "unit-testing-user"
UNIT_TESTING_PASSWORD = "unit-testing-password"
GITHUB_TESTING_USER = "github-testing-user"


@pytest.fixture(scope="module")
def create_database():
    """
    Fixture to create database and tables
    """
    SqlAlchemyBase.metadata.create_all(bind=engine)
    yield
    SqlAlchemyBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def db(create_database):
    """
    Fixture providing a database session
    :return: database session fixture.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(db) -> Generator[TestClient, None, None]:
    """
    Fixture for the FastAPI test client
    :return:
    """
    settings.ENVIRONMENT = "testing"
    with TestClient(app) as c:
        yield c
        SqlAlchemyBase.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def unit_test_user(db) -> Generator[User, Any, None]:
    """
    Fixture for creating a user in the 'SQLite test database'
    :return: the user object.
    """
    user_repository = UserRepository(db)
    test_user = user_repository.create(
        username=UNIT_TESTING_USER,
        password=Security.get_password_hash(UNIT_TESTING_PASSWORD),
        email_address="unit-test@mail.com",
        name="unit-tester",
    )

    yield user_repository.get_by_id(test_user.id)
    user_repository.delete(test_user.id)


@pytest.fixture(scope="function")
def github_user(db) -> Generator[User, Any, None]:
    """
    Fixture for creating a user in the 'SQLite test database'
    :return: the user object.
    """
    user_repository = UserRepository(db)
    github_test_user = user_repository.create(
        username=GITHUB_TESTING_USER,
        github_id=123456,
        email_address="github-user@github.com",
        name="github-user",
    )

    yield user_repository.get_by_id(github_test_user.id)
    user_repository.delete(github_test_user.id)


@pytest.fixture
def session(client, unit_test_user) -> Generator[str | None, Any, None]:
    """
    Create a session for the unit test user.
    :param unit_test_user: The mock unit test user
    :param client: the FastAPI test client
    :return:
    """
    payload = {"username": UNIT_TESTING_USER, "password": UNIT_TESTING_PASSWORD}
    result = client.post(url=f"{settings.API_V1_STR}/auth/login", json=payload)
    session_token = result.cookies.get("farmhand_user")
    client.cookies["farmhand_user"] = session_token
    yield session_token


@pytest.fixture
def mock_mod_hub_page(mocker) -> callable:
    """
    Create a fixture for a modhub page, define which HTML resource should be
    returned and what status code.
    :param mocker: pytest mocker
    :return: a callable _mock_page function
    """

    def _mock_page(file_name: Optional[str] = None, status_code: int = status.HTTP_200_OK) -> None:
        html_content = load_test_resource(file_name) if file_name else None

        mock_response = Response()
        mock_response.status_code = status_code
        if html_content:
            mock_response._content = html_content

        mocker.patch("requests.get", return_value=mock_response)

    return _mock_page


@pytest.fixture
async def mock_crop_data(mocker, db) -> None:
    """
    Fixture for mocking the crop data JSON.
    :param mocker: pytest mocker
    """
    mocker.patch(
        "src.api.services.crop_service.CropService._load_crop_data_from_fixture"
    ).return_value = crop_data()

    crop_service = CropService(db)
    await crop_service.load_crops()


@pytest.fixture
async def mock_github_login(mocker):
    """
    Mock the '/github' login and redirect request
    :param mocker: pytest-mocker
    :return: the mocked authorize_redirect object.
    """

    async def _mock_redirect(request, redirect_uri):
        """Mock the GitHub redirect"""
        return None

    return mocker.patch.object(github, "authorize_redirect", side_effect=_mock_redirect)


@pytest.fixture
async def mock_github_authentication(mocker, github_user):
    """
    Mock the GitHub authentication callback and its access token.
    :param mocker: pytest mocker
    :param github_user: the github user to mock
    """

    async def _mock_github_token_response(url, token):
        """Mock the GitHub token check"""
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "id": github_user.github_id,
            "login": github_user.username,
            "email": github_user.email_address,
            "name": github_user.name,
        }
        return mock_response

    # Mock the authorisation of the access token
    mocker.patch.object(
        github, "authorize_access_token", return_value={"access_token": "some-token"}
    )

    # Mock the authorisation of the github user and their token
    mocker.patch.object(github, "get", side_effect=_mock_github_token_response)
