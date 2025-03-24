import uuid
import datetime

from sqlalchemy import Column, UUID, String, DateTime, Boolean, Text, ForeignKey, Integer, Enum, Double
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.api.constants import FarmTypes, SoilTypes, FertilizerStates, WeedStates, FieldTypes
from src.api.core.repositories import UserRepository, Repository, FieldRepository, CropRepository


class User(UserRepository):
    """
    DB model for a user
    """

    __tablename__ = "users"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    github_id = Column(Integer, unique=True, nullable=True)
    username = Column(String(255), unique=True, nullable=False)
    email_address = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    farms = relationship("Farm", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User: {self.username}>"


class Farm(Repository):
    """
    DB Model for farms.
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

    user = relationship("User", back_populates="farms")

    map = relationship("Map", back_populates="farms")

    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Farm: {self.name}, Map: {self.map_name}>"


class Map(Repository):
    """
    DB Model for Maps.
    """

    __tablename__ = "maps"

    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    author = Column(String(100), nullable=True)
    release_date = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    farms = relationship("Farm", back_populates="map")


class Field(FieldRepository):
    """
    Base DB class for fields which store all the common attributes.
    """
    __tablename__ = "fields"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    size = Column(Double(), nullable=True)
    ground_type = Column(String(50), nullable=True)  # Ground Type Enum

    farm_id: Mapped[UUID] = mapped_column(UUID(), ForeignKey("farms.id"), nullable=False)
    farm = relationship("Farm", back_populates="fields")

    field_type = Column(Enum(FieldTypes, native_enum=False), nullable=False, default=FieldTypes.BASE_FIELD)

    crops = relationship(
        "FieldCrop",
        back_populates="field",
        order_by="desc(FieldCrop.planted_at)",
        cascade="all, delete-orphan"
    )

    plowed = Column(Boolean, nullable=True)
    rolled = Column(Boolean, nullable=True)
    weeds = Column(Enum(WeedStates, native_enum=False), nullable=True, default=WeedStates.NO_WEEDS)
    mulched = Column(Boolean, nullable=True)

    base_game_field = relationship("BaseGameField", back_populates="field", uselist=False, cascade="all, delete-orphan")
    precision_farming_field = relationship("PrecisionFarmingField", back_populates="field", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Field {self.number} in Farm {self.farm_id} | Current Crop: {self.current_crop()}>"


class BaseGameField(Repository):
    """
    DB Model for standard fields (Base Game).
    """
    __tablename__ = "base_game_fields"

    id = Column(UUID(), ForeignKey("fields.id"), primary_key=True)
    fertilized = Column(
        Enum(FertilizerStates, native_enum=False),
        nullable=False,
        default=FertilizerStates.ZER0_PERCENT
    )
    limed = Column(Boolean, nullable=True)

    field = relationship("Field", back_populates="base_game_field")

    def __repr__(self):
        return f"<BaseGameField {self.field.number}, Fertilized: {self.fertilized}, Limed: {self.limed}>"


class PrecisionFarmingField(Repository):
    """
    DB Model for fields using Precision Farming mod.
    """
    __tablename__ = "precision_farming_fields"

    id = Column(UUID(), ForeignKey("fields.id"), primary_key=True)

    nitrogen_level = Column(Integer, nullable=True)
    ph_level = Column(Double, nullable=True)
    soil_type = Column(Enum(SoilTypes, native_enum=False), nullable=True, default=SoilTypes.LOAM)

    field = relationship("Field", back_populates="precision_farming_field")

    def __repr__(self):
        return (
            f"<PrecisionFarmingField {self.field.number}, "
            f"Nitrogen: {self.nitrogen_level}, "
            f"pH: {self.ph_level}, "
            f"Soil: {self.soil_type}>"
        )


class Crop(CropRepository):
    """
    Crops available for fields.
    """

    __tablename__ = "crops"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    type = Column(String(50), unique=True, nullable=False)
    yield_per_ha = Column(Integer(), nullable=False)
    seeds_per_ha = Column(Integer(), nullable=False)
    price = Column(Double(), nullable=False)
    growth_stages = Column(Integer(), nullable=False)
    growth_duration = Column(Integer(), nullable=False)
    root_crop = Column(Boolean(), nullable=False)

    planted_in = Column(String(255), nullable=False)
    harvested_in = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Crop: {self.type}>"


class FieldCrop(Repository):
    """
    Tracks all crops ever planted on a field.
    """

    __tablename__ = "field_crops"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(), ForeignKey("fields.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    planted_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    field = relationship("Field", back_populates="crops")
    crop = relationship("Crop")

    def __repr__(self):
        return f"<FieldCrop: {self.crop.name} on Field {self.field_id} at {self.planted_at}>"
