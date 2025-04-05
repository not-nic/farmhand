from sqlalchemy import Column, Integer, String, Double, Boolean

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

    id = Column(Integer(), primary_key=True, autoincrement=True)
    type = Column(String(50), unique=True, nullable=False)
    yield_per_ha = Column(Integer(), nullable=False)
    seeds_per_ha = Column(Integer(), nullable=False)
    nitrogen_per_kg_ha = Column(Integer(), nullable=True)
    price = Column(Double(), nullable=False)
    growth_stages = Column(Integer(), nullable=False)
    growth_duration = Column(Integer(), nullable=False)
    root_crop = Column(Boolean(), nullable=False)

    planted_in = Column(String(255), nullable=False)
    harvested_in = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Crop: {self.type}>"
