from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, conint, condecimal, Field, model_validator, PrivateAttr, computed_field
from src.api.constants import FieldTypes, FertilizerStates, WeedStates, SoilTypes
from src.api.core.schema.crops.crops import CropResponse
from src.api.core.schema.validators import Validators


class FieldRequest(BaseModel):
    """
    Request model for creating a field.
    """

    number: conint(ge=0, le=1000)
    field_type: FieldTypes
    ground_type: str
    size: condecimal(ge=0, le=Decimal(1000), max_digits=6, decimal_places=2)
    owned: bool = False
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
    owned: bool
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
