import datetime
import uuid
from typing import Optional

from pydantic import BaseModel


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

