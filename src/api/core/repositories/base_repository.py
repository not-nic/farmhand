"""
Python module containing farmhand repositories.

Farmhand follows the repository pattern and each database model should
inherit from a repository and if any custom database logic is required

e.g. getting all fields that share the same crop it should be written
as a method within its own <model_name>Repository.
"""

from typing import TypeVar, Generic, Type, Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

T = TypeVar("T", bound=DeclarativeMeta)


class Repository(Generic[T]):
    """
    Base Repository class for generic CRUD database operations.
    """

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def all(self) -> List[T]:
        """
        get all items from DB using inherited class.
        :return: all items in a specific database table.
        """
        return self.db.query(self.model).all()

    def create(self, **kwargs) -> T:
        """
        Create an object in the specified DB table
        :param kwargs: kwargs: parameters to update, i.e. Model.update(id, value_1="some-id")
        :return: the created object
        """
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: Optional[UUID | int]) -> Optional[T]:
        """
        Get a single record from DB by its ID.
        :param id: id of the item to get
        :return: a single record from the database matching the associated id.
        """
        return self.db.query(self.model).get(id)

    def delete(self, id: Optional[UUID | int]) -> None:
        """
        delete an object by an ID
        :param id: the id of the record to be deleted
        :return: the deleted object
        """
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()

    def update(self, id: Optional[UUID | int], **kwargs) -> Optional[T]:
        """
        Update an existing record in the database.
        :param id: the id of the record to update.
        :param kwargs: parameters to update, i.e. Model.update(id, value_1="some-id")
        :return: the updated object, or None if the object doesn't exist
        """
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.db.commit()
            return obj
        return None

    @staticmethod
    def to_dict(obj: T):
        """
        Return a dictionary representation of the object.
        :return: dict with column names as keys and their values.
        """
        return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


