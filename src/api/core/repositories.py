"""
Python module containing farmhand repositories.

Farmhand follows the repository pattern and each database model should
inherit from a repository and if any custom database logic is required

e.g. getting all fields that share the same crop it should be written
as a method within its own <model_name>Repository.
"""

from typing import Optional, TypeVar, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from src.api.core.db import Base, db_session

if TYPE_CHECKING:
    from src.api.core.db_models import User, Field, Crop

T = TypeVar("T", bound="Repository")

sessions = {}


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


class CropRepository(Repository):
    """
    User Repository for interaction with the DB
    """

    __abstract__ = True

    @classmethod
    def get_by_type(cls: "Crop", type: str) -> Optional["Crop"]:
        """
        get a user by their username
        :param type: the type of crop.
        :return: the user that matches the username, or none.
        """
        return cls.get_session().query(cls).filter(cls.type == type).first()


class FieldRepository(Repository):
    """
    Field Repository for interacting with the DB and making queries
    """

    __abstract__ = True

    @classmethod
    def update(cls: "Field", id: Optional[UUID | int], **kwargs) -> Optional["Field"]:
        """
        Update the details of a field and any associated relationships such as base_game_fields
        or precision_farming_fields.
        :param id: ID of the field to update.
        :param kwargs: Parameters to update, e.g., {number: 123}.
        :return: The updated field object or None if not found.
        """

        field: Field = cls.get(id)
        if not field:
            return None

        for key, value in kwargs.items():
            if hasattr(field, key):
                setattr(field, key, value)

        session = cls.get_session()
        session.commit()

        base_field_values = ["fertilized", "limed"]
        precision_field_values = ["nitrogen_level", "ph_level", "soil_type"]

        # Check if the field is a base_game_field and get any kwargs from the update object and apply them.
        if field.base_game_field:
            base_field_kwargs = {key: kwargs[key] for key in base_field_values if key in kwargs}
            if base_field_kwargs:
                field.base_game_field.update(field.id, **base_field_kwargs)

        # Check if the field is a precision_farming_field and get any kwargs from the update object and apply them.
        if field.precision_farming_field:
            precision_field_kwargs = {
                key: kwargs[key] for key in precision_field_values if key in kwargs
            }
            if precision_field_kwargs:
                field.precision_farming_field.update(field.id, **precision_field_kwargs)

        session.commit()

        return field

    @classmethod
    def delete(cls: "Field", id: UUID) -> Optional[T]:
        """
        delete a field and its associated field type object by its ID
        :param id: the id of the record to be deleted
        :return: the deleted object
        """
        session = cls.get_session()
        field: Field = cls.get(id)
        if field:
            if field.base_game_field:
                field.base_game_field.delete(field.id)

            if field.precision_farming_field:
                field.precision_farming_field.delete(field.id)

            session.delete(field)
            session.commit()
        return field

    def current_crop(self: "Field") -> Optional[dict]:
        """
        Get the most recent crop planted as a dictionary.
        """
        crops_dict = self.get_crops_dict()
        return crops_dict[0] if crops_dict else None

    def past_crops(self: "Field") -> list[dict]:
        """
        Get all previous crops (excluding the current one) as dictionaries.
        """
        crops_dict = self.get_crops_dict()
        return crops_dict[1:]

    def get_crops_dict(self: "Field") -> list[dict]:
        """
        Get all crops for the field as a readable dictionary.
        """
        return [
            {
                "id": field_crop.id,
                "crop_type": field_crop.crop.type,
                "planted_at": field_crop.planted_at,
            }
            for field_crop in self.crops
        ]
