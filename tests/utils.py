"""
Utils for pytest unit tests.
"""

import json
import os.path


def load_test_resource(filename: str) -> str:
    """
    Util function to load a file from the resources' folder.
    :param filename: the filename to open
    :return: the file
    """
    filepath = os.path.join("tests", "resources", filename)
    with open(filepath) as file:
        return file.read()


def crop_data() -> list[dict]:
    """
    get crop data from test resource
    :return: (list[dict]) of crop data.
    """
    return json.loads(load_test_resource("test_crop_data.json"))
