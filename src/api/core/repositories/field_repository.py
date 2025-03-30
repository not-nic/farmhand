"""
Field Repository containing field database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from src.api.core.repositories.base_repository import Repository

if TYPE_CHECKING:
    from src.api.core.db_models import Field


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
    def delete(cls: "Field", id: UUID) -> Optional["Field"]:
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
