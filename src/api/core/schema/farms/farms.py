from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.api.constants import FarmTypes
from src.api.core.schema.validators import Validators


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
