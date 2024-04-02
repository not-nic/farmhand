from sqlalchemy import Column, Integer, ForeignKey, Boolean, Enum
import enum
from app import database


class CropType(enum.Enum):
    WHEAT = 'wheat'
    BARLEY = 'barley'
    CANOLA = 'canola'
    OAT = 'oat'
    CORN = 'corn'
    SUNFLOWERS = 'sunflowers'
    SOYBEANS = 'soybeans'
    POTATOES = 'potatoes'
    SUGAR_BEET = 'sugar beet'
    SORGHUM = 'sorghum'
    POPLAR = 'poplar'
    GRASS = 'grass'
    OILSEED_RADISH = 'oilseed radish'
    RED_BEET = 'red beet'
    CARROTS = 'carrots'
    PARSNIPS = 'parsnip'


class Crop(database.Model):
    id = Column(Integer, primary_key=True)
    type = Column(Enum(CropType), nullable=False)
    growth_stage = Column(Integer, nullable=False)
    is_previous = Column(Boolean, nullable=False)
    field_id = Column(Integer, ForeignKey('field.number'), nullable=False)