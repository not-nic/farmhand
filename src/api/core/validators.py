import datetime
import re


class Validators:
    @staticmethod
    def validate_release_date(value) -> datetime:
        """
        Pydantic Validator to validate the release date of a mod into a date object.
        :param value: (str) of a date
        :return: (date) object of the incoming date
        """
        if isinstance(value, str):
            try:
                return datetime.datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {value}. Expected format is 'dd.mm.yyyy'.")
        return value

    @staticmethod
    def validate_size(value) -> float:
        """
        Pydantic Validator to validate the size of a mod into MBs.
        :param value: the filesize of the mod
        :return: the size in MB
        """
        match = re.match(r"^(\d+(\.\d+)?)\s*(KB|MB)$", value.strip(), re.IGNORECASE)

        if match:
            size = float(match.group(1))
            unit = match.group(3).upper()

            if unit == "KB":
                return size / 1024
            return size

        raise ValueError(
            f"Invalid size format: {value}. Expected format is '<number> KB' or '<number> MB'."
        )

    @staticmethod
    def validate_platform(value) -> list:
        """
        Pydantic Validator to split the platforms a mod is available on into a list
        :param value: the list of platforms as a string
        :return: platforms as a list
        """
        return [platform.strip() for platform in value.split(",")]

    @staticmethod
    def validate_map_id_or_name_exists(values):
        """
        Pydantic Validator to check that either a map_id or map_name exists
        in the FarmRequest object.
        :param values: the values of the incoming object
        :return: Validation Error if neither are provided.
        """
        map_id = values.get('map_id')
        map_name = values.get('map_name')
        if not map_id and not map_name:
            raise ValueError('Either `map_id` or `map_name` must be provided.')
        return values
