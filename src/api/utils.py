"""
Farmhand util functions.
"""

from typing import Union

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


def format_pydantic_errors(
    validation_error: Union[ValidationError | RequestValidationError],
) -> dict:
    """
    Util function to nicely format pydantic validation errors.
    :param validation_error: Pydantic ValidationError
    :return: (dict) error message 'detail' response
    """
    errors = validation_error.errors()
    if errors:
        messages = [err.get("msg", "Validation error") for err in errors]
        return {"detail": "; ".join(messages)}
    return {"detail": "Unknown validation error"}
