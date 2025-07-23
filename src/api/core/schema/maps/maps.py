"""
Module containing pydantic models for maps.
"""
from datetime import date

from pydantic import BaseModel


class MapModel(BaseModel):
    """
    Pydantic model for a Farming Simulator Map.
    """
    id: int
    name: str
    category: str
    author: str
    release_date: date
    version: str
