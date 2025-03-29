"""
Pydantic Validation and Serialisation models used in the Farmhand
request routes and services.
"""

from typing import Optional, Union

from datetime import datetime, date
from uuid import UUID
from pydantic import (
    BaseModel,
    field_validator,
    field_serializer,
    model_validator,
    Field,
    conint,
    condecimal,
    computed_field,
    PrivateAttr,
)
from decimal import Decimal

from src.api.constants import (
    FarmTypes,
    WeedStates,
    FertilizerStates,
    SoilTypes,
    FieldTypes,
    AuthTypes,
)
from src.api.core.serializers import Serializers
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


class TokenModel(BaseModel):
    """
    pydantic model for the JWT Token used in the username/password login and github
    authentication.
    """

    id: Union[int, UUID]
    auth_type: AuthTypes = Field(default=AuthTypes.DEFAULT)
    expires_at: datetime = Field(alias="exp")
    issued_at: datetime = Field(alias="iat")

    @field_serializer("expires_at", "issued_at")
    def serialize_expires_and_issued_at_values(self, value):
        return Serializers.serialize_datetime(value)

    class Config:
        populate_by_name = True
        by_alias = True


class GithubUser(BaseModel):
    """
    Pydantic model for a user that has authenticated with GitHub.
    """

    id: int
    username: str = Field(alias="login")
    name: str
    email: Optional[str] = None

    @model_validator(mode="after")
    def validate_github_email(self):
        Validators.validate_github_email_if_not_exists(self)

    class Config:
        populate_by_name = True


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

    id: UUID
    name: str
    farm_type: FarmTypes
    map_name: str
    map_id: Optional[int]
    description: str
    created_at: datetime


class FarmsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """

    farms: list[FarmResponse]
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


class CropRequest(BaseModel):
    """
    Pydantic model for creating (planting) a crop in a field.
    """

    crop_type: str = Field(alias="type")
    ground_type: Optional[str] = None


class CropResponse(BaseModel):
    """
    Response model for returning a FieldCrop that's associated with a Farm and Field.
    """

    id: UUID
    crop_type: str
    planted_at: datetime


class CropsResponse(BaseModel):
    """
    Response model for returning multiple field crops.
    """

    crops: list[CropResponse]
    count: Optional[int] = None


class FieldRequest(BaseModel):
    """
    Request model for creating a field.
    """

    number: conint(ge=0, le=1000)
    field_type: FieldTypes
    ground_type: str
    size: condecimal(ge=0, le=Decimal(1000), max_digits=6, decimal_places=2)
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


class PrecisionFarmingFieldModel(BaseModel):
    """
    Pydantic Response model for a 'Precision Farming' field.
    """

    nitrogen_level: Optional[int] = None
    ph_level: Optional[float] = None
    soil_type: Optional[SoilTypes] = None


class BaseGameFieldModel(BaseModel):
    """
    Pydantic Response model for a 'Base Game' field.
    """

    limed: Optional[bool] = None
    fertilized: Optional[FertilizerStates] = None


class FieldResponse(BaseModel):
    """
    Field Response model containing

    """

    id: UUID
    created_at: datetime
    number: int
    ground_type: str
    size: float
    plowed: bool
    rolled: bool
    mulched: bool
    weeds: WeedStates = Field(default=WeedStates.NO_WEEDS)

    __base_field: Optional[BaseGameFieldModel] = PrivateAttr(default=None)
    __precision_field: Optional[PrecisionFarmingFieldModel] = PrivateAttr(default=None)

    def set_base_field(self, base_field: BaseGameFieldModel):
        self.__base_field = base_field

    def set_precision_field(self, precision_field: PrecisionFarmingFieldModel):
        self.__precision_field = precision_field

    crop: CropResponse = None

    @computed_field
    @property
    def limed(self) -> Optional[bool]:
        return self.__base_field.limed if self.__base_field else None

    @computed_field
    @property
    def fertilized(self) -> Optional[FertilizerStates]:
        return self.__base_field.fertilized if self.__base_field else None

    @computed_field
    @property
    def nitrogen_level(self) -> Optional[int]:
        return self.__precision_field.nitrogen_level if self.__precision_field else None

    @computed_field
    @property
    def ph_level(self) -> Optional[float]:
        return self.__precision_field.ph_level if self.__precision_field else None

    @computed_field
    @property
    def soil_type(self) -> Optional[str]:
        return self.__precision_field.soil_type if self.__precision_field else None

    class Config:
        exclude_none = True


class FieldsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """

    fields: list[FieldResponse]
    count: int


class FieldUpdate(BaseModel):
    """
    Request model for updating a field.
    """

    number: Optional[conint(ge=0, le=1000)] = None
    ground_type: Optional[str] = None
    size: Optional[condecimal(ge=0, le=Decimal(1000), max_digits=6, decimal_places=2)] = None
    plowed: Optional[bool] = None
    rolled: Optional[bool] = None
    mulched: Optional[bool] = None
    limed: Optional[bool] = None
    fertilized: Optional[FertilizerStates] = None
    weeds: Optional[WeedStates] = None
    nitrogen_level: Optional[int] = None
    ph_level: Optional[float] = None
    soil_type: Optional[SoilTypes] = None
