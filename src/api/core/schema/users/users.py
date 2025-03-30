from typing import Optional

from pydantic import BaseModel, Field, model_validator

from src.api.core.schema.validators import Validators


class UserCreate(BaseModel):
    """
    Request model for creating a new user.
    """

    username: str
    email_address: str
    password: str
    name: str


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
