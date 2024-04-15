from sqlalchemy import Column, Integer, Double, Boolean, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import database
from models.field_crop import FieldCrop


class Field(database.Model):
    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    number = Column(Integer, nullable=False, unique=True)

    crops = relationship(FieldCrop, backref='field', lazy=True)

    ground_type = Column(String(255), nullable=True)
    soil_type = Column(String(255), nullable=True)

    nitrogen_level = Column(Integer, nullable=True)
    ph_level = Column(Double, nullable=True)

    plowed = Column(Boolean, nullable=True)
    rolled = Column(Boolean, nullable=True)
    weeded = Column(Boolean, nullable=True)
    mulched = Column(Boolean, nullable=True)

