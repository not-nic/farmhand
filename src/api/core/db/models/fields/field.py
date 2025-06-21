from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, Integer, DateTime, Double, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.constants import FieldTypes, WeedStates
from src.api.core.db.models._model_base import SqlAlchemyBase

if TYPE_CHECKING:
    from src.api.core.db.models import Farm, FieldCrop, BaseGameField, PrecisionFarmingField


class Field(SqlAlchemyBase):
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

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    size: Mapped[float] = mapped_column(Double, nullable=True, default=0.0)
    ground_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Ground Type Enum
    owned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    farm_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("farms.id"), nullable=False)
    farm: Mapped["Farm"] = relationship("Farm", back_populates="fields")

    field_type: Mapped[FieldTypes] = mapped_column(
        Enum(FieldTypes, native_enum=False), nullable=False, default=FieldTypes.BASE_FIELD
    )

    crops: Mapped[list["FieldCrop"]] = relationship(
        "FieldCrop",
        back_populates="field",
        order_by="desc(FieldCrop.planted_at)",
        cascade="all, delete-orphan",
    )

    plowed: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    rolled: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    mulched: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

    weeds: Mapped[WeedStates] = mapped_column(
        Enum(WeedStates, native_enum=False), nullable=True, default=WeedStates.NO_WEEDS
    )

    base_game_field: Mapped["BaseGameField"] = relationship(
        "BaseGameField",
        back_populates="field",
        uselist=False,
        cascade="all, delete-orphan"
    )

    precision_farming_field: Mapped["PrecisionFarmingField"] = relationship(
        "PrecisionFarmingField",
        back_populates="field",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Field {self.number} in Farm {self.farm_id} | Current Crop: {self.current_crop()}>"

    def current_crop(self) -> Optional["FieldCrop"]:
        """
        Get the most recent crop planted as a dictionary.
        """
        return self.crops[0] if self.crops else []

    def past_crops(self: "Field") -> List["FieldCrop"]:
        """
        Get all previous crops (excluding the current one) as dictionaries.
        """
        return self.crops[1:]

    def get_crops(self) -> List["FieldCrop"]:
        """
        Get all crops for the field as a readable dictionary.
        """
        return self.crops
