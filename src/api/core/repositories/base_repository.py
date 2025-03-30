"""
Python module containing farmhand repositories.

Farmhand follows the repository pattern and each database model should
inherit from a repository and if any custom database logic is required

e.g. getting all fields that share the same crop it should be written
as a method within its own <model_name>Repository.
"""

from typing import Optional, TypeVar
from uuid import UUID
from sqlalchemy.orm import Session

from src.api.core.db import Base, db_session

T = TypeVar("T", bound="Repository")


class Repository(Base):
    """
    Repository class to provide re-usable interactions with DB, all models should inherit from here (see models.py).
        i.e. Model(Repository)
                -> Model.create(...)
    """

    __abstract__ = True

    @classmethod
    def get_session(cls) -> Session:
        """Get the current session"""
        return db_session

    @classmethod
    def all(cls) -> list:
        """
        get all items from DB using inherited class.
        :return: all items in a specific database table.
        """
        session = cls.get_session()
        return session.query(cls).all()

    @classmethod
    def get(cls, id: Optional[UUID | int]) -> Optional[T]:
        """
        Get a single record from DB by its ID.
        :param id: id of the item to get
        :return: a single record from the database matching the associated id.
        """
        session = cls.get_session()
        return session.query(cls).get(id)

    @classmethod
    def create(cls, **kwargs) -> Optional[T]:
        """
        Create an object in the specified DB table
        :param kwargs: kwargs: parameters to update, i.e. Model.update(id, value_1="some-id")
        :return: the created object
        """
        session = cls.get_session()
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()
        return obj

    @classmethod
    def delete(cls, id: UUID) -> Optional[T]:
        """
        delete an object by an ID
        :param id: the id of the record to be deleted
        :return: the deleted object
        """
        session = cls.get_session()
        obj = cls.get(id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj

    @classmethod
    def update(cls, id: Optional[UUID | int], **kwargs) -> Optional[T]:
        """
        Update an existing record in the database.
        :param id: the id of the record to update.
        :param kwargs: parameters to update, i.e. Model.update(id, value_1="some-id")
        :return: the updated object, or None if the object doesn't exist
        """
        session = cls.get_session()
        obj = cls.get(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            session.commit()
            return obj
        return None

    def to_dict(self):
        """
        Return a dictionary representation of the object.
        :return: dict with column names as keys and their values.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

