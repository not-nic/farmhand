"""
Python Module containing base SqlAlchemy classes and mixins for common methods
like to_dict.
"""

from typing import TypeVar

from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound="BaseMixin")


class BaseMixin:
    """
    Mixin class for models to inherit from to provide base methods or attributes.
    """

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the SQLAlchemy model instance.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class SqlAlchemyBase(BaseMixin, DeclarativeBase):
    pass
