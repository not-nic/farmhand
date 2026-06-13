"""
User Repository containing user database interactions.
see: base_repository.py to see the base repository to inherit from.
"""


from sqlalchemy.orm import Session

from src.api.core.db.models import User
from src.api.core.repositories.base_repository import Repository


class UserRepository(Repository[User]):
    """
    User Repository for interaction with the DB
    """

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_username(self, username: str) -> User | None:
        """
        get a user by their username
        :param username:
        :return: the user that matches the username, or none.
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        """
        get a user by their email
        :param email: the users email
        :return: the user that matches the email, or none.
        """
        return self.db.query(User).filter(User.email_address == email).first()

    def get_by_github_id(self, github_id: int) -> User | None:
        """
        get a user by their email
        :param github_id: the users GitHub ID.
        :return: the user that matches the email, or none.
        """
        return self.db.query(User).filter(User.github_id == github_id).first()
