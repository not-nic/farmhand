import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator, Field, conint, condecimal
from decimal import Decimal

from src.api.constants import FarmTypes, WeedStates, FertilizerStates, SoilTypes, FieldTypes
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


class FarmRequest(BaseModel):
    """
    Request model for creating a farm.
    """

    name: str
    description: str
    farm_type: FarmTypes = Field(default=FarmTypes.BASE)
    map_name: Optional[str] = None
    map_id: Optional[int] = None

    @model_validator(mode="before")
    def validate_map_id_or_name(cls, values):
        return Validators.validate_map_id_or_name_exists(values)


class FarmUpdate(FarmRequest):
    """
    Request model for creating a farm.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    map_name: Optional[str] = None


class FarmResponse(BaseModel):
    """
    Response model for returning a singular farm.
    """

    id: uuid.UUID
    name: str
    farm_type: FarmTypes
    map_name: str
    map_id: Optional[int]
    description: str
    created_at: datetime.datetime


class FarmsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """

    farms: list[FarmResponse]
    count: int


class FieldRequest(BaseModel):
    """
    Request model for creating a field.
    """

    number: conint(ge=0, le=99999)
    field_type: FieldTypes
    ground_type: str
    size: condecimal(ge=0, le=Decimal(999.999), max_digits=6, decimal_places=3)
    plowed: bool
    rolled: bool
    mulched: bool
    limed: Optional[bool] = None
    fertilized: Optional[FertilizerStates] = None
    weeds: WeedStates = Field(default=WeedStates.NO_WEEDS)
    nitrogen_level: Optional[int] = None
    ph_level: Optional[float] = None
    soil_type: Optional[SoilTypes] = None

    class Config:
        exclude_none = True

    @model_validator(mode="before")
    def validate_field_model(cls, values):
        return Validators.validate_field_request_model(values)


class FieldResponse(BaseModel):
    """
    Response Model for returning a Base Game / Precision Farming Field.
    """

    id: uuid.UUID
    number: int
    ground_type: str
    size: float
    plowed: bool
    rolled: bool
    mulched: bool
    limed: Optional[bool] = None
    fertilized: Optional[FertilizerStates] = None

    nitrogen_level: Optional[int] = None
    ph_level: Optional[float] = None
    soil_type: Optional[SoilTypes] = None

    weeds: WeedStates = Field(default=WeedStates.NO_WEEDS)
    created_at: datetime.datetime


class FieldsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """

    fields: list[FieldResponse]
    count: int


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


class CropModel(BaseModel):
    """
    Pydantic model for Farming Simulator Crops.
    """

    type: str
    yield_per_ha: int
    seeds_per_ha: int
    price: float

    growth_stages: int
    growth_duration: int
    root_crop: bool

    planted_in: str
    harvested_in: str

    @field_validator("planted_in", "harvested_in", mode="before")
    def validate_months(cls, value):
        return Validators.validate_months(value)
