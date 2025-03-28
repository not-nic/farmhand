"""
Python Module for the Farmhand database models using the SQLAlchemy ORM.
"""

import uuid
import datetime

from sqlalchemy import (
    Column,
    UUID,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Integer,
    Enum,
    Double,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.api.constants import FarmTypes, SoilTypes, FertilizerStates, WeedStates, FieldTypes
from src.api.core.repositories import UserRepository, Repository, FieldRepository, CropRepository


class User(UserRepository):
    """
    Database Model for the User.

    Attributes:
        id: the UUID of the user.
        github_id: the GitHub ID of the user (only populated if signed up with GitHub OAuth).
        username: the username of the user.
        email_address: the email_address of the user.
        password: the hashed password of the user.
        name: the name of the user.
        created_at: the timestamp the user was created.
        is_active: boolean for if the user is active.

    Required fields when creating a new user: username, email_address, password, name.
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

    user = relationship("User", back_populates="farms")

    map = relationship("Map", back_populates="farms")

    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Farm: {self.name}, Map: {self.map_name}>"


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


class Field(FieldRepository):
    """
    Database Model for a Field.

    Attributes:
        id: the UUID of the field.
        number: The field number
        created_at: Timestamp of when the field was created
        size: The size of the map in Hectares
        ground_type: The current field ground type.
        farm_id: the id of the farm the field belongs too
        field_type: the type of field (Base Game or Precision Farming)
        plowed: boolean if the field is plowed.
        rolled: boolean if the field is rolled.
        mulched: boolean if the field is mulched.
        weeds: Value of the type of weeds in the field (0 - None, 1 - Small, 2 - Medium, 3 - Large, 4 - Sprayed)

    Required fields when creating a new field: number.
    """

    __tablename__ = "fields"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    size = Column(Double(), nullable=True)
    ground_type = Column(String(50), nullable=True)  # Ground Type Enum

    farm_id: Mapped[UUID] = mapped_column(UUID(), ForeignKey("farms.id"), nullable=False)
    farm = relationship("Farm", back_populates="fields")

    field_type = Column(
        Enum(FieldTypes, native_enum=False), nullable=False, default=FieldTypes.BASE_FIELD
    )

    crops = relationship(
        "FieldCrop",
        back_populates="field",
        order_by="desc(FieldCrop.planted_at)",
        cascade="all, delete-orphan",
    )

    plowed = Column(Boolean, nullable=True)
    rolled = Column(Boolean, nullable=True)
    mulched = Column(Boolean, nullable=True)
    weeds = Column(Enum(WeedStates, native_enum=False), nullable=True, default=WeedStates.NO_WEEDS)

    base_game_field = relationship(
        "BaseGameField", back_populates="field", uselist=False, cascade="all, delete-orphan"
    )
    precision_farming_field = relationship(
        "PrecisionFarmingField", back_populates="field", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Field {self.number} in Farm {self.farm_id} | Current Crop: {self.current_crop()}>"


class BaseGameField(Repository):
    """
    Database Model for a BaseGameField.

    Attributes:
        id: the UUID of the base game field.
        fertilized: The fertilized state (0 - None, 50 - 50% fertilized, 100 - 100% fertilized)
        limed: boolean if the field is limed,
        field: The field this is related too.

    Required fields when creating a new base game field: fertilized, limed, field.
    """

    __tablename__ = "base_game_fields"

    id = Column(UUID(), ForeignKey("fields.id"), primary_key=True)
    fertilized = Column(
        Enum(FertilizerStates, native_enum=False),
        nullable=False,
        default=FertilizerStates.ZER0_PERCENT,
    )
    limed = Column(Boolean, nullable=True)

    field = relationship("Field", back_populates="base_game_field")

    def __repr__(self):
        return f"<BaseGameField {self.field.number}, Fertilized: {self.fertilized}, Limed: {self.limed}>"


class PrecisionFarmingField(Repository):
    """
    Database Model for a PrecisionFarmingField.

    Attributes:
        id: the UUID of the precision farming field.
        nitrogen_level: The nitrogen level of the field in kg/ha
        ph_level: the ph level of the field
        soil_type: the soil type of the field: (Silty Clay, Loam, Sandy Loam, Loamy Sand)
        field: The field this is related too.

    Required fields when creating a new base game field: nitrogen_level, ph_level, soil_type.
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
    Database Model for a Crop.

    Attributes:
        id: the auto-incremented integer.
        type: the type of crop e.g. wheat, barley etc.
        yield_per_ha: the yield per hectare.
        seeds_per_ha: the seeds required per hectare.
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
    Database Model for a FieldCrop, which tracks all crops planted in
    an associated field.

    Attributes:
        id: the auto-incremented integer.
        field_id: the field the crop is planted in.
        crop_id: the id of the crop planted in the field.
        planted_at: the timestamp of when the crop was planted.

    Required fields when creating a new crop: field_id, crop_id.
    """

    __tablename__ = "field_crops"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(), ForeignKey("fields.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    planted_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    field = relationship("Field", back_populates="crops")
    crop = relationship("Crop")

    def __repr__(self):
        return (
            f"<FieldCrop: {self.crop.type} "
            f"on Field {self.field.number} ({self.field_id}) "
            f"planted at {self.planted_at}>"
        )
