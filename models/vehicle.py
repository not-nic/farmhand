from sqlalchemy import Column, Integer, String
from app import database


class Vehicle(database.Model):
    id = Column(Integer, primary_key=True)
    model = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    img_url = Column(String(255), nullable=True)
    price = Column(Integer, nullable=False)
    power = Column(Integer, nullable=True, default=0)
