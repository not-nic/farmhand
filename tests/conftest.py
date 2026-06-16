"""
Pytest conftest.py containing test setup, TestClient Fixtures and other mocks.
"""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from main import app
from src.api.core.db import SessionLocal, engine
from src.api.core.db.models import User
from src.api.core.db.models._model_base import SqlAlchemyBase
from src.api.core.repositories import UserRepository
from src.api.core.security import Security, github
from src.api.services.crop_service import CropService
from src.config import settings
from tests.utils import crop_data

pytest_plugins = "tests.fixtures"

UNIT_TESTING_USER = "unit-testing-user"
UNIT_TESTING_PASSWORD = "unit-testing-password"
GITHUB_TESTING_USER = "github-testing-user"


@pytest.fixture(scope="session")
def db():
    """
    Fixture providing a database session
    :return: database session fixture.
    """
    SqlAlchemyBase.metadata.drop_all(bind=engine)
    SqlAlchemyBase.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(db, make_httpserver):
    """
    Fixture for a FastAPI test client.
    """
    settings.DATA_API_URL = make_httpserver.url_for("")
    return TestClient(app)


@pytest.fixture(scope="session")
def unit_test_user(db) -> Generator[User, Any]:
    """
    Fixture for creating a user in the 'SQLite test database'
    :return: The user object.
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


@pytest.fixture(scope="session")
def github_user(db) -> Generator[User, Any]:
    """
    Fixture for creating a user in the 'SQLite test database'
    :return: The user object.
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


@pytest.fixture(scope="session")
def session(client, unit_test_user) -> Generator[str | None, Any]:
    """
    Create a session for the unit test user.
    :param unit_test_user: The mock unit test user
    :param client: The FastAPI test client
    :return: the session token
    """
    payload = {"username": UNIT_TESTING_USER, "password": UNIT_TESTING_PASSWORD}
    result = client.post(url=f"{settings.API_V1_STR}/auth/login", json=payload)
    session_token = result.cookies.get("farmhand_user")
    client.cookies["farmhand_user"] = session_token
    yield session_token


@pytest.fixture(scope="session")
def user_id(unit_test_user) -> Any:
    """
    Fixture for the user_id of the unit testing account.
    :return: (UUID) unit test user id
    """
    return unit_test_user.id


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

    mocker.patch.object(
        github, "authorize_access_token", return_value={"access_token": "some-token"}
    )
    mocker.patch.object(github, "get", side_effect=_mock_github_token_response)
