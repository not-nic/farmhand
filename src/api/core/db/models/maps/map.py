from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.api.core.db.models._model_base import SqlAlchemyBase

if TYPE_CHECKING:
    from src.api.core.db.models import Farm


class Map(SqlAlchemyBase):
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    author: Mapped[str] = mapped_column(String(100), nullable=True)
    release_date: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0.0", nullable=False)

    farms: Mapped[list["Farm"]] = relationship("Farm", back_populates="map")
