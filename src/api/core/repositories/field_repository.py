"""
Field Repository containing field database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

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

    def update_obj(self, field: Field, **kwargs) -> Field:
        """
        Update the details of a field and any associated relationships such as base_game_fields
        or precision_farming_fields.
        :param field: The field instance to update.
        :param kwargs: Parameters to update, e.g. {number: 123}.
        :return: The updated field object.
        """
        for key, value in kwargs.items():
            if hasattr(field, key):
                setattr(field, key, value)

        base_field_values = ["fertilized", "limed"]
        precision_field_values = ["nitrogen_level", "ph_level", "soil_type"]

        if field.base_game_field:
            base_field_kwargs = {key: kwargs[key] for key in base_field_values if key in kwargs}
            if base_field_kwargs:
                base_game_field_repo = Repository(self.db, BaseGameField)
                base_game_field_repo.update(field.base_game_field, **base_field_kwargs)

        if field.precision_farming_field:
            precision_field_kwargs = {key: kwargs[key] for key in precision_field_values if key in kwargs}
            if precision_field_kwargs:
                precision_farming_field_repo = Repository(self.db, PrecisionFarmingField)
                precision_farming_field_repo.update(field.precision_farming_field, **precision_field_kwargs)

        self.db.commit()
        return field

    def delete_obj(self, field: Field) -> Field:
        """
        Delete a field and its associated field type object.
        :param field: The field instance to delete.
        :return: The deleted field object.
        """
        if field.base_game_field:
            self.db.delete(field.base_game_field)

        if field.precision_farming_field:
            self.db.delete(field.precision_farming_field)

        self.db.delete(field)
        self.db.commit()
        return field

    def get_field_by_number(self, number: int, farm_id: UUID) -> Field | None:
        """
        Get a field from a farm by its field number.
        :param number: the number of the field.
        :param farm_id: the id of the farm.
        return: (Field) the requested field if exists else None.
        """
        stmt = select(Field).where(and_(Field.number == number, Field.farm_id == farm_id))
        return self.db.execute(stmt).scalars().first()
