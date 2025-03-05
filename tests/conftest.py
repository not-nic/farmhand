import pytest

from collections.abc import Generator
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv("tests/fixtures/test.env", override=True)

from main import app
from main import settings
from src.api.core.db import Base, engine
from src.api.core.models import User
from src.api.core.security import Security


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
def create_test_user():
    """
    Fixture for creating a user in the 'SQLite test database'
    :return: the user object.
    """
    test_user = User.create(
        username="unit-testing-user",
        password=Security.get_password_hash("unit-testing-password"),
        email_address="unit-test@mail.com",
        name="unit-tester"
    )

    return User.get(test_user.id)

