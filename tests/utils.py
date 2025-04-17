"""
Utils for pytest unit tests.
"""

import json
import os.path
from typing import Optional

from starlette.testclient import TestClient


class TestClientHelper:
    """
    Test client helper class for post, put, get and delete.
    """

    @staticmethod
    def post(url: str, json: Optional[dict], client: TestClient):
        """
        POST request helper.
        :param url: the url to test
        :param json: the json payload to send
        :param client: the TestClient instance to use
        :return: the response from the API.
        """
        return client.post(url, json=json)

    @staticmethod
    def put(url: str, json: dict, client: TestClient):
        """
        PUT request helper.
        :param url: the url to test
        :param json: the json payload to send
        :param client: the TestClient instance to use
        :return: the response from the API.
        """
        return client.put(url, json=json)

    @staticmethod
    def get(url: str, client: TestClient):
        """
        GET request helper.
        :param url: the url to test
        :param client: the TestClient instance to use
        :return: the response from the API.
        """
        return client.get(url)

    @staticmethod
    def delete(url: str, client: TestClient):
        """
        Delete request helper.
        :param url: the url to test
        :param client: the TestClient instance to use
        :return: the response from the API.
        """
        return client.delete(url)


def load_test_resource(filename: str) -> str:
    """
    Util function to load a file from the resources' folder.
    :param filename: the filename to open
    :return: the file
    """
    filepath = os.path.join("tests", "resources", filename)
    with open(filepath, "r") as file:
        return file.read()


def crop_data() -> list[dict]:
    """
    get crop data from test resource
    :return: (list[dict]) of crop data.
    """
    return json.loads(load_test_resource("test_crop_data.json"))