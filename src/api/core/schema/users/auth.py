from datetime import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from src.api.constants import AuthTypes
from src.api.core.schema.serializers import Serializers


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
