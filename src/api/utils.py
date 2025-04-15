"""
Farmhand util functions.
"""


def parse_version(v: str) -> list:
    """
    Parse the version of a mod and split it on each part.
    :param v: (str) mod version
    :return: a list of the integer parts.
    """
    return [int(part) for part in v.split('.')]
