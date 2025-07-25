from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.api.core.schema.validators import Validators


class CropModel(BaseModel):
    """
    Pydantic model for Farming Simulator Crops.
    """

    type: str
    yield_per_ha: int
    seeds_per_ha: int
    nitrogen_per_kg_ha: Optional[int]
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
