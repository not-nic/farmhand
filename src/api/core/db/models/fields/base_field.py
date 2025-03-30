from sqlalchemy import Column, UUID, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from src.api.constants import FertilizerStates
from src.api.core.repositories import Repository


class BaseGameField(Repository):
    """
    Database Model for a BaseGameField.

    Attributes:
        id: the UUID of the base game field.
        fertilized: The fertilized state (0 - None, 50 - 50% fertilized, 100 - 100% fertilized)
        limed: boolean if the field is limed,
        field: The field this is related too.

    Required fields when creating a new base game field: fertilized, limed, field.
    """

    __tablename__ = "base_game_fields"

    id = Column(UUID(), ForeignKey("fields.id"), primary_key=True)
    fertilized = Column(
        Enum(FertilizerStates, native_enum=False),
        nullable=False,
        default=FertilizerStates.ZER0_PERCENT,
    )
    limed = Column(Boolean, nullable=True)

    field = relationship("Field", back_populates="base_game_field")

    def __repr__(self):
        return f"<BaseGameField {self.field.number}, Fertilized: {self.fertilized}, Limed: {self.limed}>"
