"""
User Repository containing user database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from typing import Optional, TYPE_CHECKING

from src.api.core.repositories.base_repository import Repository

if TYPE_CHECKING:
    from src.api.core.db.models.users import User


class UserRepository(Repository):
    """
    User Repository for interaction with the DB
    """

    __abstract__ = True

    @classmethod
    def get_by_username(cls: "User", username: str) -> Optional["User"]:
        """
        get a user by their username
        :param username:
        :return: the user that matches the username, or none.
        """
        return cls.get_session().query(cls).filter(cls.username == username).first()

    @classmethod
    def get_by_email(cls: "User", email: str) -> Optional["User"]:
        """
        get a user by their email
        :param email: the users email
        :return: the user that matches the email, or none.
        """
        return cls.get_session().query(cls).filter(cls.email_address == email).first()

    @classmethod
    def get_by_github_id(cls: "User", github_id: int) -> Optional["User"]:
        """
        get a user by their email
        :param github_id: the users GitHub ID.
        :return: the user that matches the email, or none.
        """
        return cls.get_session().query(cls).filter(cls.github_id == github_id).first()
