from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    computed_field,
    condecimal,
    conint,
    model_validator,
)

from src.api.constants import FertilizerStates, FieldTypes, SoilTypes, WeedStates
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
    limed: bool | None = None
    fertilized: FertilizerStates | None = None
    weeds: WeedStates = Field(default=WeedStates.NO_WEEDS)
    nitrogen_level: int | None = None
    ph_level: float | None = None
    soil_type: SoilTypes | None = None

    class Config:
        exclude_none = True

    @model_validator(mode="before")
    def validate_field_model(cls, values):
        return Validators.validate_field_request_model(values)


class PrecisionFarmingFieldModel(BaseModel):
    """
    Pydantic Response model for a 'Precision Farming' field.
    """

    nitrogen_level: int | None = None
    ph_level: float | None = None
    soil_type: SoilTypes | None = None


class BaseGameFieldModel(BaseModel):
    """
    Pydantic Response model for a 'Base Game' field.
    """

    limed: bool | None = None
    fertilized: FertilizerStates | None = None


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

    __base_field: BaseGameFieldModel | None = PrivateAttr(default=None)
    __precision_field: PrecisionFarmingFieldModel | None = PrivateAttr(default=None)

    def set_base_field(self, base_field: BaseGameFieldModel):
        self.__base_field = base_field

    def set_precision_field(self, precision_field: PrecisionFarmingFieldModel):
        self.__precision_field = precision_field

    crop: CropResponse = None

    @computed_field
    @property
    def limed(self) -> bool | None:
        return self.__base_field.limed if self.__base_field else None

    @computed_field
    @property
    def fertilized(self) -> FertilizerStates | None:
        return self.__base_field.fertilized if self.__base_field else None

    @computed_field
    @property
    def nitrogen_level(self) -> int | None:
        return self.__precision_field.nitrogen_level if self.__precision_field else None

    @computed_field
    @property
    def ph_level(self) -> float | None:
        return self.__precision_field.ph_level if self.__precision_field else None

    @computed_field
    @property
    def soil_type(self) -> str | None:
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

    number: conint(ge=0, le=1000) | None = None
    ground_type: str | None = None
    size: condecimal(ge=0, le=Decimal(1000), max_digits=6, decimal_places=2) | None = None
    owned: bool | None = None
    plowed: bool | None = None
    rolled: bool | None = None
    mulched: bool | None = None
    limed: bool | None = None
    fertilized: FertilizerStates | None = None
    weeds: WeedStates | None = None
    nitrogen_level: int | None = None
    ph_level: float | None = None
    soil_type: SoilTypes | None = None
