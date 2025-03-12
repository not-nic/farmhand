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
