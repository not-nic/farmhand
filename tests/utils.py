"""
Utils for pytest unit tests.
"""

import os.path


def load_test_resource(filename: str) -> str:
    """
    Util function to load a file from the resources' folder.
    :param filename: the filename to open
    :return: the file
    """
    filepath = os.path.join("tests", "resources", filename)
    with open(filepath, "r") as file:
        return file.read()


def crop_data():
    return [
        {
            "type": "Wheat",
            "yield_per_ha": 8900,
            "seeds_per_ha": 500,
            "nitrogen_per_kg_ha": 200,
            "price": 0.377,
            "growth_stages": 7,
            "growth_duration": 10,
            "root_crop": False,
            "planted_in": "September, October",
            "harvested_in": "July, August, September",
        },
        {
            "type": "Barley",
            "yield_per_ha": 9600,
            "seeds_per_ha": 500,
            "nitrogen_per_kg_ha": 200,
            "price": 0.313,
            "growth_stages": 6,
            "growth_duration": 9,
            "root_crop": False,
            "planted_in": "September, October",
            "harvested_in": "June, July",
        },
        {
            "type": "Maize",
            "yield_per_ha": 9200,
            "seeds_per_ha": 400,
            "nitrogen_per_kg_ha": 200,
            "price": 0.808,
            "growth_stages": 6,
            "growth_duration": 6,
            "root_crop": True,
            "planted_in": "April, May",
            "harvested_in": "October, November",
        },
    ]
