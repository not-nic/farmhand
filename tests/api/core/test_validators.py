"""
Python module containing unit tests for validator functions.
"""

import pytest

from src.api.core.schema.users import GithubUser
from src.api.core.schema.validators import Validators


class TestValidators:
    def test_validate_farm_request_with_map_id(self):
        """
        test that when given a map_id value the farm request is validated.
        """
        values = {"map_id": "1234"}
        result = Validators.validate_map_id_or_name_exists(values)
        assert result == values

    def test_validate_farm_request_with_map_name(self):
        """
        test that when given a map_name value the farm request is validated.
        """
        values = {"map_name": "Forest"}
        result = Validators.validate_map_id_or_name_exists(values)
        assert result == values

    def test_validate_farm_request_with_both_values(self):
        """
        test that when given a map_name value the farm request is validated.
        """
        values = {"map_id": "1234", "map_name": "Forest"}
        result = Validators.validate_map_id_or_name_exists(values)
        assert result == values

    def test_validate_farm_request_with_no_values(self):
        """
        test that when given neither a map_name nor map_id a value error is raised.
        """
        values = {"description": "value"}
        with pytest.raises(ValueError, match="Either `map_id` or `map_name` must be provided."):
            Validators.validate_map_id_or_name_exists(values)

    def test_validate_months(self):
        """
        Test that when given a list of months its split into a comma separated string.
        """
        months = ["August", "September", "October"]
        expected_output = "August, September, October"
        assert Validators.validate_months(months) == expected_output

        input_string = "January, February, March"
        assert Validators.validate_months(input_string) == input_string
        assert Validators.validate_months([]) == ""

    def test_validate_field_request_model_pass(self):
        """
        Test that when given the correct field values separately
        the validation is correct.
        """
        precision_farming_values = {"nitrogen_level": 50, "ph_level": 6.5, "soil_type": "loamy"}

        base_game_values = {"numberfertilized": True, "limed": False}

        assert (
            Validators.validate_field_request_model(precision_farming_values)
            == precision_farming_values
        )
        assert Validators.validate_field_request_model(base_game_values) == base_game_values

    def test_validate_field_request_model_fail(self):
        """
        Test that the validator raises a ValueError when both values of fields
        are used together.
        """
        invalid_input = {
            "nitrogen_level": 50,
            "ph_level": 6.5,
            "soil_type": "loamy",
            "fertilized": True,
        }

        with pytest.raises(
            ValueError,
            match="Precision Farming field values.*cannot be used with Base Game Field.* ",
        ):
            Validators.validate_field_request_model(invalid_input)

    def test_validate_github_email_if_exists(self):
        """
        Test that when validating an existing email it remains unchanged.
        """
        user = GithubUser(id=1234, login="spegg", email="simon-pegg@hotfuzz.com", name="simon pegg")
        assert user.email == "simon-pegg@hotfuzz.com"

    def test_validate_github_email_if_not_exists(self):
        """
        Test that a GitHub email is created when one does not exist.
        """
        user = GithubUser(id=1234, login="spegg", name="simon pegg")
        assert user.email == "spegg@github.com"
