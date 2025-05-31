import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, UUID, Integer, DateTime, Double, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.constants import FieldTypes, WeedStates
from src.api.core.repositories import FieldRepository

if TYPE_CHECKING:
    from src.api.core.db.models import BaseGameField, PrecisionFarmingField


class Field(FieldRepository):
    """
    Database Model for a Field.

    Attributes:
        id: the UUID of the field.
        number: The field number
        created_at: Timestamp of when the field was created
        size: The size of the map in Hectares
        ground_type: The current field ground type.
        farm_id: the id of the farm the field belongs too
        field_type: the type of field (Base Game or Precision Farming)
        plowed: boolean if the field is plowed.
        rolled: boolean if the field is rolled.
        mulched: boolean if the field is mulched.
        weeds: Value of the type of weeds in the field (0 - None, 1 - Small, 2 - Medium, 3 - Large, 4 - Sprayed)

    Required fields when creating a new field: number.
    """

    __tablename__ = "fields"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    number = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    size = Column(Double, nullable=True)
    ground_type = Column(String(50), nullable=True)  # Ground Type Enum
    owned = Column(Boolean, nullable=False, default=False)
    farm_id: Mapped[UUID] = mapped_column(UUID(), ForeignKey("farms.id"), nullable=False)
    farm = relationship("Farm", back_populates="fields")

    field_type = Column(
        Enum(FieldTypes, native_enum=False), nullable=False, default=FieldTypes.BASE_FIELD
    )

    crops = relationship(
        "FieldCrop",
        back_populates="field",
        order_by="desc(FieldCrop.planted_at)",
        cascade="all, delete-orphan",
    )

    plowed = Column(Boolean, nullable=True)
    rolled = Column(Boolean, nullable=True)
    mulched = Column(Boolean, nullable=True)
    weeds = Column(Enum(WeedStates, native_enum=False), nullable=True, default=WeedStates.NO_WEEDS)

    base_game_field: Mapped["BaseGameField"] = relationship(
        "BaseGameField", back_populates="field", uselist=False, cascade="all, delete-orphan"
    )
    precision_farming_field: Mapped["PrecisionFarmingField"] = relationship(
        "PrecisionFarmingField", back_populates="field", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Field {self.number} in Farm {self.farm_id} | Current Crop: {self.current_crop()}>"
