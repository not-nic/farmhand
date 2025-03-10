import pytest

from collections.abc import Generator
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv("tests/fixtures/test.env", override=True)

# ruff: noqa: E402
from main import app
from main import settings
from src.api.core.db import Base, engine
from src.api.core.db_models import User
from src.api.core.security import Security


UNIT_TESTING_USER = "unit-testing-user"
UNIT_TESTING_PASSWORD = "unit-testing-password"


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
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
