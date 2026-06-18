"""
Python module containing Farm Request / Response Pydantic Models.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.api.constants import Difficulty, FarmTypes


class FarmRequest(BaseModel):
    """
    Request model for creating a farm.
    """
    model_config = ConfigDict(extra="forbid")

    farm_type: FarmTypes = Field(default=FarmTypes.BASE)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)
    map_id: int


class FarmUpdate(BaseModel):
    """
    Request model for creating a farm.
    """
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    difficulty: Difficulty | None = None


class FarmResponse(BaseModel):
    """
    Response model for returning a singular farm.
    """
    model_config = ConfigDict(from_attributes=True)

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
