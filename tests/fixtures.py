"""
Fixtures module for reusable pytest fixtures to be used across tests.
"""
from typing import Tuple

import pytest
import datetime

from uuid import UUID

from src.api.constants import FarmTypes, FieldTypes, SoilTypes, WeedStates, FertilizerStates
from src.api.core.db_models import User, Map, Farm, Field, BaseField, PrecisionFarmingField
from tests.conftest import UNIT_TESTING_USER


@pytest.fixture
def farms(user_id) -> list[Farm]:
    farms = [
        Farm.create(
            name="farm 1",
            description="description 1",
            map_name="map 1",
            owner_id=user_id
        ),
        Farm.create(
            name="farm 2",
            description="description 2",
            farm_type=FarmTypes.PRECISION_FARMING,
            map_name="map 3",
            owner_id=user_id
        )
    ]
    return farms


@pytest.fixture
def farm_map():
    expected_map = Map.create(
        id=12345,
        name="custom-map-1",
        category="European Map",
        author="Simon Pegg",
        release_date=datetime.date(year=2025, month=3, day=11)
    )
    return expected_map


@pytest.fixture
def user_id() -> UUID:
    return User.get_by_username(UNIT_TESTING_USER).id


@pytest.fixture
def fields(farms) -> Tuple[list[Field], list[Field]]:
    base_fields = [
        BaseField.create(
            number=1,
            size=15,
            ground_type="planted",
            farm_id=farms[0].id,
            field_type=FieldTypes.BASE_FIELD,
            plowed=True,
            rolled=True,
            mulched=False,
            weeds=WeedStates.MEDIUM_WEEDS,
            fertilized=FertilizerStates.FIFTY_PERCENT,
            limed=True
        ),
        BaseField.create(
            number=2,
            size=20,
            ground_type="growing",
            farm_id=farms[0].id,
            field_type=FieldTypes.BASE_FIELD,
            plowed=True,
            rolled=True,
            mulched=False,
            weeds=WeedStates.MEDIUM_WEEDS,
            fertilized=FertilizerStates.FIFTY_PERCENT,
            limed=True
        ),
        BaseField.create(
            number=3,
            size=10.5,
            ground_type="ready to harvest",
            farm_id=farms[0].id,
            field_type=FieldTypes.BASE_FIELD,
            plowed=True,
            rolled=True,
            mulched=False,
            weeds=WeedStates.MEDIUM_WEEDS,
            fertilized=FertilizerStates.FIFTY_PERCENT,
            limed=True
        )
    ]

    precision_fields = [
        PrecisionFarmingField.create(
            number=1,
            size=15,
            ground_type="planted",
            farm_id=farms[1].id,
            field_type=FieldTypes.PRECISION_FARMING_FIELD,
            plowed=True,
            rolled=True,
            mulched=False,
            weeds=WeedStates.MEDIUM_WEEDS,
            nitrogen_level=100,
            ph_level=5.0,
            soil_type=SoilTypes.SANDY_LOAM
        ),
        PrecisionFarmingField.create(
            number=2,
            size=20,
            ground_type="growing",
            farm_id=farms[1].id,
            field_type=FieldTypes.PRECISION_FARMING_FIELD,
            plowed=True,
            rolled=True,
            mulched=False,
            weeds=WeedStates.MEDIUM_WEEDS,
            nitrogen_level=100,
            ph_level=5.0,
            soil_type=SoilTypes.LOAM
        ),
        PrecisionFarmingField.create(
            number=3,
            size=10.5,
            ground_type="ready to harvest",
            farm_id=farms[1].id,
            field_type=FieldTypes.PRECISION_FARMING_FIELD,
            plowed=True,
            rolled=True,
            mulched=False,
            weeds=WeedStates.MEDIUM_WEEDS,
            nitrogen_level=100,
            ph_level=5.0,
            soil_type=SoilTypes.SILTY_CLAY
        )
    ]

    return base_fields, precision_fields
