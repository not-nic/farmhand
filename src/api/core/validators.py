import datetime
import re


class Validators:
    @staticmethod
    def validate_release_date(value) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {value}. Expected format is 'dd.mm.yyyy'.")
        return value

    @staticmethod
    def validate_size(value) -> float:
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
        return [platform.strip() for platform in value.split(",")]

    @staticmethod
    def validate_map_id_or_name_exists(values):
        map_id = values.get('map_id')
        map_name = values.get('map_name')
        if not map_id and not map_name:
            raise ValueError('Either `map_id` or `map_name` must be provided.')
        return values
