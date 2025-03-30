import datetime
import uuid

from sqlalchemy import Column, UUID, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

from src.api.core.repositories import Repository


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

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(), ForeignKey("fields.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    planted_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    field = relationship("Field", back_populates="crops")
    crop = relationship("Crop")

    def __repr__(self):
        return (
            f"<FieldCrop: {self.crop.type} "
            f"on Field {self.field.number} ({self.field_id}) "
            f"planted at {self.planted_at}>"
        )
