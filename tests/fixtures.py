"""
Fixtures module for reusable pytest fixtures to be used across tests.
"""

from decimal import Decimal

import pytest
import datetime

from uuid import UUID

from src.api.constants import FarmTypes, FieldTypes, SoilTypes, WeedStates, FertilizerStates
from src.api.core.db.models.maps import Map
from src.api.core.db.models.farms import Farm
from src.api.core.db.models.users import User
from src.api.core.schema.fields import FieldRequest, FieldResponse
from src.api.services.field_service import FieldService
from tests.conftest import UNIT_TESTING_USER


@pytest.fixture
def farms(user_id) -> list[Farm]:
    farms = [
        Farm.create(name="farm 1", description="description 1", map_name="map 1", owner_id=user_id),
        Farm.create(
            name="farm 2",
            description="description 2",
            farm_type=FarmTypes.PRECISION_FARMING,
            map_name="map 3",
            owner_id=user_id,
        ),
    ]
    return farms


@pytest.fixture
def farm_map():
    expected_map = Map.create(
        id=12345,
        name="custom-map-1",
        category="European Map",
        author="Simon Pegg",
        release_date=datetime.date(year=2025, month=3, day=11),
    )
    return expected_map


@pytest.fixture
def user_id() -> UUID:
    return User.get_by_username(UNIT_TESTING_USER).id


@pytest.fixture
def fields(farms) -> tuple[list[FieldResponse], list[FieldResponse]]:
    """
    Pytest Fixture for generating fields associated with a Farm.
    :param farms: the farms to link fields to
    """
    field_service = FieldService()

    base_fields = [
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=1,
                size=Decimal(15.0),
                ground_type="planted",
                field_type=FieldTypes.BASE_FIELD,
                plowed=True,
                rolled=True,
                mulched=True,
                weeds=WeedStates.NO_WEEDS,
                fertilized=FertilizerStates.ONE_HUNDRED_PERCENT,
                limed=True,
            ),
            current_farm=farms[0],
        ),
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=2,
                size=Decimal(20.0),
                ground_type="growing",
                field_type=FieldTypes.BASE_FIELD,
                plowed=True,
                rolled=True,
                mulched=False,
                weeds=WeedStates.MEDIUM_WEEDS,
                fertilized=FertilizerStates.FIFTY_PERCENT,
                limed=True,
            ),
            current_farm=farms[0],
        ),
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=3,
                size=Decimal(10.5),
                ground_type="ready to harvest",
                field_type=FieldTypes.BASE_FIELD,
                plowed=True,
                rolled=True,
                mulched=False,
                weeds=WeedStates.MEDIUM_WEEDS,
                fertilized=FertilizerStates.FIFTY_PERCENT,
                limed=True,
            ),
            current_farm=farms[0],
        ),
    ]

    precision_fields = [
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=1,
                size=Decimal(15.0),
                ground_type="planted",
                field_type=FieldTypes.PRECISION_FARMING_FIELD,
                plowed=True,
                rolled=True,
                mulched=True,
                weeds=WeedStates.NO_WEEDS,
                nitrogen_level=200,
                ph_level=6.500,
                soil_type=SoilTypes.SANDY_LOAM,
            ),
            current_farm=farms[1],
        ),
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=2,
                size=Decimal(20.0),
                ground_type="growing",
                field_type=FieldTypes.PRECISION_FARMING_FIELD,
                plowed=True,
                rolled=True,
                mulched=False,
                weeds=WeedStates.MEDIUM_WEEDS,
                nitrogen_level=100,
                ph_level=5.0,
                soil_type=SoilTypes.LOAM,
            ),
            current_farm=farms[1],
        ),
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=3,
                size=Decimal(10.5),
                ground_type="ready to harvest",
                field_type=FieldTypes.PRECISION_FARMING_FIELD,
                plowed=True,
                rolled=True,
                mulched=False,
                weeds=WeedStates.MEDIUM_WEEDS,
                nitrogen_level=100,
                ph_level=5.0,
                soil_type=SoilTypes.SILTY_CLAY,
            ),
            current_farm=farms[1],
        ),
    ]

    return base_fields, precision_fields
