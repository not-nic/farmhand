from collections.abc import Generator
from fastapi.testclient import TestClient
from main import app

import pytest

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Fixture for the FastAPI test client
    :return:
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def create_test_user():
    """
    Fixture for creating a user in the 'fake_users_db'
    :return:
    """
    fake_users_db = {
        "unit-testing-user": {
            "password": "unit-testing-password",
            "name": "unit-testing"
        }
    }
    return fake_users_db
