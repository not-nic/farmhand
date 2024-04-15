from sqlalchemy import Column, Integer, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
import enum
from app import database
from models.crop import Crop


class GrowthTense(enum.Enum):
    PAST = 'past'
    PRESENT = "present"
    FUTURE = "future"


class FieldCrop(database.Model):
    id = Column(Integer, primary_key=True)
    type = Column(String(255), ForeignKey('crop.crop_type'), nullable=False)
    growth_stage = Column(Integer, nullable=False, default=1)
    growth_tense = Column(Enum(GrowthTense), nullable=False)
    field_id = Column(Integer, ForeignKey('field.number'), nullable=False)
    crop = relationship(Crop, backref="field_crop", lazy=True)
