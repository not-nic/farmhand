"""
Field Repository containing field database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.api.core.db.models.fields import BaseGameField, Field, PrecisionFarmingField
from src.api.core.repositories import Repository


class FieldRepository(Repository[Field]):
    """
    Field Repository for interacting with the DB and making queries
    """

    def __init__(self, db: Session):
        super().__init__(db, Field)

    def update(self, id: Optional[UUID | int], **kwargs) -> Optional[Field]:
        """
        Update the details of a field and any associated relationships such as base_game_fields
        or precision_farming_fields.
        :param id: ID of the field to update.
        :param kwargs: Parameters to update, e.g., {number: 123}.
        :return: The updated field object or None if not found.
        """

        field: Field = self.get_by_id(id)
        if not field:
            return None

        for key, value in kwargs.items():
            if hasattr(field, key):
                setattr(field, key, value)

        self.db.commit()

        base_field_values = ["fertilized", "limed"]
        precision_field_values = ["nitrogen_level", "ph_level", "soil_type"]

        # Check if the field is a base_game_field and get any kwargs from the update object and apply them.
        if field.base_game_field:
            base_field_kwargs = {key: kwargs[key] for key in base_field_values if key in kwargs}
            if base_field_kwargs:
                base_game_field_repo = Repository(self.db, BaseGameField)
                base_game_field_repo.update(field.id, **base_field_kwargs)

        # Check if the field is a precision_farming_field and get any kwargs from the update object and apply them.
        if field.precision_farming_field:
            precision_field_kwargs = {
                key: kwargs[key] for key in precision_field_values if key in kwargs
            }
            if precision_field_kwargs:
                precision_farming_field_repo = Repository(self.db, PrecisionFarmingField)
                precision_farming_field_repo.update(field.id, **precision_field_kwargs)

        self.db.commit()

        return field

    def delete(self, id: UUID) -> Optional[Field]:
        """
        delete a field and its associated field type object by its ID
        :param id: the id of the record to be deleted
        :return: the deleted object
        """
        field: Field = self.get_by_id(id)
        if field:
            if field.base_game_field:
                self.db.delete(field.base_game_field)

            if field.precision_farming_field:
                self.db.delete(field.precision_farming_field)

            self.db.delete(field)
            self.db.commit()
        return field

    def get_field_by_number(self, number: int, farm_id: UUID) -> Optional[Field]:
        """
        Get a field from a farm by its field number.
        :param number: the number of the field.
        :param farm_id: the id of the farm.
        return: (Field) the requested field if exists else None.
        """
        stmt = select(Field).where(and_(Field.number == number, Field.farm_id == farm_id))
        return self.db.execute(stmt).scalars().first()
