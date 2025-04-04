import datetime
import uuid

from sqlalchemy import Column, UUID, String, Text, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from src.api.constants import FarmTypes, Difficulty
from src.api.core.repositories import Repository


class Farm(Repository):
    """
    Database Model for a User's Farm.

    Attributes:
        id: the UUID of the Farm.
        name: the user generated name of the farm.
        description: the long description of the farm
        map_name: the name of the map they are playing on.
        created_at: timestamp the farm was created.
        owner_id: the user who owns the farm.
        map_id: the id of the map they are playing on (if scraped).
        farm_type: type of farm which defines which fields can be created (Base Game vs Precision Farming).

    Required fields when creating a new farm: name, map_name or map_id and owner_id.
    """

    __tablename__ = "farms"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    map_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    owner_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    map_id = Column(Integer(), ForeignKey("maps.id"), nullable=True)

    farm_type = Column(Enum(FarmTypes, native_enum=False), nullable=False, default=FarmTypes.BASE)

    difficulty = Column(Enum(Difficulty, native_enum=False), nullable=False, default=Difficulty.MEDIUM)

    user = relationship("User", back_populates="farms")
    map = relationship("Map", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Farm: {self.name}, Map: {self.map_name}>"
