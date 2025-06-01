from typing import TYPE_CHECKING
from uuid import uuid4
from datetime import datetime
from sqlalchemy import UUID, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.api.core.repositories import Repository

if TYPE_CHECKING:
    from src.api.core.db.models import Field, Crop


class FieldCrop(Repository):
    """
    Database Model for a FieldCrop, which tracks all crops planted in
    an associated field.

    Attributes:
        id: the auto-incremented integer.
        field_id: the field the crop is planted in.
        crop_id: the id of the crop planted in the field.
        planted_at: the timestamp of when the crop was planted.

    Required fields when creating a new crop: field_id, crop_id.
    """

    __tablename__ = "field_crops"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    field_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("fields.id"), nullable=False)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), nullable=False)
    planted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    field: Mapped["Field"] = relationship("Field", back_populates="crops")
    crop: Mapped["Crop"] = relationship("Crop")

    def __repr__(self):
        return (
            f"<FieldCrop: {self.crop.type} "
            f"on Field {self.field.number} ({self.field_id}) "
            f"planted at {self.planted_at}>"
        )
