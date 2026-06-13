from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.api.constants import Difficulty, FarmTypes
from src.api.core.schema.validators import Validators


class FarmRequest(BaseModel):
    """
    Request model for creating a farm.
    """

    name: str
    description: str
    farm_type: FarmTypes = Field(default=FarmTypes.BASE)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)
    map_name: str | None = None
    map_id: int | None = None

    @model_validator(mode="before")
    def validate_map_id_or_name(cls, values):
        return Validators.validate_map_id_or_name_exists(values)


class FarmUpdate(FarmRequest):
    """
    Request model for creating a farm.
    """

    name: str | None = None
    description: str | None = None
    map_name: str | None = None


class FarmResponse(BaseModel):
    """
    Response model for returning a singular farm.
    """

    id: UUID
    name: str
    farm_type: FarmTypes
    map_name: str
    map_id: int | None
    description: str
    created_at: datetime
    difficulty: Difficulty


class FarmsResponse(BaseModel):
    """
    Response model for returning a list of farms.
    """

    farms: list[FarmResponse]
    count: int
