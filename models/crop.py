from sqlalchemy import Column, String, Integer, Double, Boolean
from app import database


class Crop(database.Model):
    id = Column(Integer, primary_key=True)

    crop_type = Column(String(255), nullable=False, unique=True)

    nitrogen_level = Column(Integer, nullable=False)
    growth_stages = Column(Integer, nullable=False)
    yield_per_ha = Column(Integer, nullable=False)
    seeds_per_ha = Column(Integer, nullable=False)

    price_per_tonne = Column(Double, nullable=False)

    root_crop = Column(Boolean, default=False)
