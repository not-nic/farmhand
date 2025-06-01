
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Double, Boolean

from src.api.core.repositories import CropRepository


class Crop(CropRepository):
    """
    Database Model for a Crop.

    Attributes:
        id: the auto-incremented integer.
        type: the type of crop e.g. wheat, barley etc.
        yield_per_ha: the yield per hectare.
        seeds_per_ha: the seeds required per hectare.
        nitrogen_per_kg_ha: The 'perfect' nitrogen per kg/ha for a crop.
        price: the base price of the crop (Hard difficulty).
        growth_stages: the stages of its growth.
        growth_duration: how long it takes to grow in months.
        root_crop: boolean if this is a root crop.
        planted_in: the months it can be planted in.
        harvested_in: the months it can be harvested in.

    Required fields when creating a new crop: All values.
    """

    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    yield_per_ha: Mapped[int] = mapped_column(Integer, nullable=False)
    seeds_per_ha: Mapped[int] = mapped_column(Integer, nullable=False)
    nitrogen_per_kg_ha: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price: Mapped[float] = mapped_column(Double, nullable=False)
    growth_stages: Mapped[int] = mapped_column(Integer, nullable=False)
    growth_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    root_crop: Mapped[bool] = mapped_column(Boolean, nullable=False)
    planted_in: Mapped[str] = mapped_column(String(255), nullable=False)
    harvested_in: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<Crop: {self.type}>"
