from typing import Optional

import pytest

from collections.abc import Generator

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi import status
from fastapi.testclient import TestClient
from requests import Response

from tests.utils import load_test_resource, crop_data

load_dotenv("tests/resources/test.env", override=True)

# ruff: noqa: E402
from main import app
from main import settings
from src.api.core.db import Base, engine
from src.api.core.db_models import User
from src.api.core.security import Security

UNIT_TESTING_USER = "unit-testing-user"
UNIT_TESTING_PASSWORD = "unit-testing-password"


@pytest.fixture(scope="module")
def create_database():
    """
    Fixture to create database and tables
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client(create_database) -> Generator[TestClient, None, None]:
    """
    Fixture for the FastAPI test client
    :return:
    """
    settings.ENVIRONMENT = "testing"

    with TestClient(app) as c:
        yield c
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def create_test_user() -> User:
    """
    Fixture for creating a user in the 'SQLite test database'
    :return: the user object.
    """
    test_user = User.create(
        username=UNIT_TESTING_USER,
        password=Security.get_password_hash(UNIT_TESTING_PASSWORD),
        email_address="unit-test@mail.com",
        name="unit-tester"
    )

    yield User.get(test_user.id)
    User.delete(test_user.id)


@pytest.fixture
def session(client, create_test_user) -> str:
    """
    Create a session for the unit test user.
    :param create_test_user:
    :param client:
    :return:
    """
    payload = {"username": UNIT_TESTING_USER, "password": UNIT_TESTING_PASSWORD}
    result = client.post(url=f"{settings.API_V1_STR}/login", json=payload)
    session_token = result.cookies.get("session")
    client.cookies["session"] = session_token
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
def mock_crop_data(mocker) -> None:
    """
    Fixture for mocking the crop data JSON.
    :param mocker: pytest mocker
    """
    mocker.patch("src.api.services.crop_service.CropService._load_crop_data_from_fixture").return_value = crop_data()
