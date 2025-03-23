import datetime
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.api.core.models import GithubUser

class Validators:
    """
    Farmhand Data validators to be used alongside the pydantic models.
    """

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
        map_id = values.get("map_id")
        map_name = values.get("map_name")
        if not map_id and not map_name:
            raise ValueError("Either `map_id` or `map_name` must be provided.")
        return values

    @staticmethod
    def validate_months(value) -> str:
        """
        Validator to split months from a list into a string of months separated by a ','
        :param value: the crops months list
        :return: (str) of crop months
        """
        if isinstance(value, list):
            return ", ".join(value)
        return value

    @staticmethod
    def validate_field_request_model(values):
        """
        Validator to ensure that a Base game field request doesn't contain precision farming field values
        and vice versa.
        :param values: the request object to check values for.
        :return: the field_request model of a raise a Value Error.
        """
        nitrogen_level = values.get("nitrogen_level")
        ph_level = values.get("ph_level")
        soil_type = values.get("soil_type")
        fertilized = values.get("fertilized")
        limed = values.get("limed")

        precision_farming_fields = [nitrogen_level, ph_level, soil_type]
        base_field_fields = [fertilized, limed]

        if any(precision_farming_fields) and any(base_field_fields):
            raise ValueError(
                "Precision Farming field values (nitrogen_level, ph_level, soil_type) "
                "cannot be used with Base Game Field specific fields (fertilized, limed)."
            )

        return values

    @staticmethod
    def validate_github_email_if_not_exists(github_user: "GithubUser"):
        """
        Validator to create a GitHub email if one does not exist by
        appending the username to a @github.com domain.
        :return: the GitHub user object.
        """
        if not github_user.email:
            github_user.email = f"{github_user.username}@github.com"

        return github_user
