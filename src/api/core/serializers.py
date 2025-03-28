"""
Module for Farmhand Data serializers to be used alongside the pydantic models.
"""

from datetime import datetime


class Serializers:
    """
    Class for serializers used when serializing pydantic models into JSON.
    """

    @staticmethod
    def serialize_datetime(value: datetime) -> int:
        """
        serialize a datetime object into a timestamp that can be used in
        JWT tokens.
        :param value: the value expiry date / issued at as a datetime object.
        :return: an integer value of the timestamp.
        """
        if isinstance(value, datetime):
            return int(value.timestamp())
        raise ValueError(f"Expected datetime, got {type(value)}")
