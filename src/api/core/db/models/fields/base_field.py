from typing import TYPE_CHECKING
from sqlalchemy import UUID, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.api.constants import FertilizerStates
from src.api.core.db.models._model_base import SqlAlchemyBase

if TYPE_CHECKING:
    from src.api.core.db.models import Field


class BaseGameField(SqlAlchemyBase):
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

    id: Mapped[UUID] = mapped_column(UUID, ForeignKey("fields.id"), primary_key=True)
    fertilized: Mapped[FertilizerStates] = mapped_column(
        Enum(FertilizerStates, native_enum=False),
        nullable=False,
        default=FertilizerStates.ZER0_PERCENT,
    )
    limed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    field: Mapped["Field"] = relationship("Field", back_populates="base_game_field")

    def __repr__(self):
        return f"<BaseGameField {self.field.number}, Fertilized: {self.fertilized}, Limed: {self.limed}>"
