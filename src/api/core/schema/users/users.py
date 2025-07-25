"""
Python module containing pydantic models for Users.
"""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


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
        """
        set a default @github.com email if no email is found in scopes.
        :return: GithubUser Pydantic model.
        """
        self.email = self.email or f"{self.username}@github.com"
        return self

    class Config:
        populate_by_name = True
