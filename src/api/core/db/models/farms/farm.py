from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.constants import Difficulty, FarmTypes
from src.api.core.db.models._model_base import SqlAlchemyBase

if TYPE_CHECKING:
    from src.api.core.db.models import Field, Task, User


class Farm(SqlAlchemyBase):
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

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    map_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    owner_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    map_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    farm_type: Mapped[FarmTypes] = mapped_column(
        Enum(FarmTypes, native_enum=False), nullable=False, default=FarmTypes.BASE
    )

    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, native_enum=False), nullable=False, default=Difficulty.MEDIUM
    )

    user: Mapped["User"] = relationship("User", back_populates="farms")

    fields: Mapped[list["Field"]] = relationship(
        "Field", back_populates="farm", cascade="all, delete-orphan"
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="farm", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Farm: {self.name}, Map: {self.map_name}>"
