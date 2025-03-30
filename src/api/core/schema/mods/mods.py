from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.api.core.schema.validators import Validators


class ModModel(BaseModel):
    """
    Pydantic model for a Farming Simulator Mod Hub mod.
    """

    id: int
    name: str
    game: str = Field(..., alias="Game")
    manufacturer: str = Field(..., alias="Manufacturer")
    category: str = Field(..., alias="Category")
    author: str = Field(..., alias="Author")
    size: str = Field(..., alias="Size")
    version: str = Field(..., alias="Version")
    release_date: Optional[date | str] = Field(..., alias="Released")
    platform: Optional[list | str] = Field(..., alias="Platform")

    @field_validator("release_date")
    def validate_release_date(cls, value):
        return Validators.validate_release_date(value)

    @field_validator("size")
    def validate_size(cls, value):
        return Validators.validate_size(value)

    @field_validator("platform")
    def validate_platform(cls, value):
        return Validators.validate_platform(value)
