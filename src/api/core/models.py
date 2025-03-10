import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, field_validator, Field

from src.api.core.validators import Validators


class LoginRequest(BaseModel):
    """
    Request model for logging into the service.
    """

    username: str
    password: str


class UserCreate(BaseModel):
    """
    Request model for creating a new user.
    """

    username: str
    email_address: str
    password: str
    name: str


class FarmCreate(BaseModel):
    """
    Request model for creating a farm.
    """

    name: str
    description: str
    map: str


class FarmUpdate(FarmCreate):
    """
    Request model for creating a farm.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    map: Optional[str] = None


class FarmResponse(BaseModel):
    """
    Response model for returning a singular farm.
    """

    id: uuid.UUID
    name: str
    map: str
    description: str
    created_at: datetime.datetime


class FarmsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """

    farms: list[FarmResponse]
    count: int


class Mod(BaseModel):
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
    release_date: Optional[datetime.date | str] = Field(..., alias="Released")
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