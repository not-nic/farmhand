"""
Module for testing the farmhand data serialization classes
"""

from datetime import datetime

import pytest

from src.api.core.schema.serializers import Serializers


class TestSerializers:
    def test_serialize_datetime_with_valid_datetime(self):
        """
        Test serialize_datetime with a valid datetime object.
        """
        time_stamp = datetime(2019, 5, 1, 16, 30, 0)
        result = Serializers.serialize_datetime(time_stamp)

        assert isinstance(result, int)
        assert result == int(time_stamp.timestamp())

    def test_serialize_date_time_with_invalid_types(self):
        """
        Test serialize_datetime with invalid types to ensure a ValidationError is raised.
        """
        invalid_inputs = ["24-03-2025", 123456789, None, {}, []]

        for input_value in invalid_inputs:
            with pytest.raises(ValueError, match="Expected datetime, got"):
                Serializers.serialize_datetime(input_value)
