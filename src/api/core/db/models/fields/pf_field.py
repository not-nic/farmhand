from typing import TYPE_CHECKING

from sqlalchemy import UUID, Double, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.constants import SoilTypes
from src.api.core.db.models._model_base import SqlAlchemyBase

if TYPE_CHECKING:
    from src.api.core.db.models import Field


class PrecisionFarmingField(SqlAlchemyBase):
    """
    Database Model for a PrecisionFarmingField.

    Attributes:
        id: the UUID of the precision farming field.
        nitrogen_level: The nitrogen level of the field in kg/ha
        ph_level: the ph level of the field
        soil_type: the soil type of the field: (Silty Clay, Loam, Sandy Loam, Loamy Sand)
        field: The field this is related too.

    Required fields when creating a new base game field: nitrogen_level, ph_level, soil_type.
    """

    __tablename__ = "precision_farming_fields"

    id: Mapped[UUID] = mapped_column(UUID, ForeignKey("fields.id"), primary_key=True)
    nitrogen_level: Mapped[int] = mapped_column(Integer, nullable=True)
    ph_level: Mapped[float] = mapped_column(Double, nullable=True)
    soil_type: Mapped[SoilTypes] = mapped_column(
        Enum(SoilTypes, native_enum=False), nullable=True, default=SoilTypes.LOAM
    )

    field: Mapped[Field] = relationship("Field", back_populates="precision_farming_field")

    def __repr__(self):
        return (
            f"<PrecisionFarmingField {self.field.number}, "
            f"Nitrogen: {self.nitrogen_level}, "
            f"pH: {self.ph_level}, "
            f"Soil: {self.soil_type}>"
        )
