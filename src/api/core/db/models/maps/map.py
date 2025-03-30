import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from src.api.core.repositories import Repository


class Map(Repository):
    """
    Database Model for a ModHub Map.

    Attributes:
        id: the ModHub ID of the Map.
        name: The Map name.
        category: The category on ModHub the map is in.
        author: The Author of the map.
        release_date: The date the map was released.
        created_at: timestamp the map was created.

    Required fields when creating a new map: id and name.
    """

    __tablename__ = "maps"

    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    author = Column(String(100), nullable=True)
    release_date = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    farms = relationship("Farm", back_populates="map")
