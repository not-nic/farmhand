"""
Fixtures module for reusable pytest fixtures to be used across tests.
"""

from decimal import Decimal

import pytest
import datetime

from uuid import UUID

from src.api.constants import FarmTypes, FieldTypes, SoilTypes, WeedStates, FertilizerStates
from src.api.core.db.models import Field, User
from src.api.core.db.models.maps import Map
from src.api.core.db.models.farms import Farm
from src.api.core.repositories import UserRepository, FarmRepository, FieldRepository, MapRepository
from src.api.core.schema.fields import FieldRequest, FieldResponse
from src.api.services.field_service import FieldService
from src.api.services.tasks_service import TaskService
from tests.conftest import UNIT_TESTING_USER


@pytest.fixture
def farms(user_id, db) -> list[Farm]:
    """
    Fixture containing farms for the unit test user.
    :param user_id: the unit test user id
    :return: a list of farms.
    """
    farm_repository = FarmRepository(db)
    farms = [
        farm_repository.create(
            name="farm 1",
            description="description 1",
            map_name="map 1",
            owner_id=user_id
        ),
        farm_repository.create(
            name="farm 2",
            description="description 2",
            farm_type=FarmTypes.PRECISION_FARMING,
            map_name="map 3",
            owner_id=user_id,
        ),
    ]
    return farms


@pytest.fixture
def farm(farms) -> Farm:
    """
    Fixture of a single farm
    :param farms: farms fixture
    :return: (Farm) a farm
    """
    return farms[0]


@pytest.fixture
def farm_map(db):
    """
    Fixture of a ModHub map
    """
    map_repository = MapRepository(db)
    expected_map: Map = map_repository.create(
        id=123456,
        name="custom-map-1",
        category="European Map",
        author="Simon Pegg",
        release_date=datetime.date(year=2025, month=3, day=11),
        version="1.0.0.0"
    )
    return expected_map


@pytest.fixture
def user_id(db) -> UUID:
    """
    Fixture for the user_id of the unit testing account.
    :return: (UUID) unit test user id
    """
    user_repository = UserRepository(db)
    user: User = user_repository.get_by_username(UNIT_TESTING_USER)
    return user.id


@pytest.fixture
def base_game_fields(farms: list[Farm], db) -> list[FieldResponse]:
    """
    Fixture containing a list of base game fields.
    :return: list(FieldResponse) of base game fields.
    """
    field_service = FieldService(db)
    return [
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=1,
                size=Decimal(15.0),
                owned=True,
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
                owned=True,
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
                owned=True,
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


@pytest.fixture
def precision_farming_fields(farms, db) -> list[FieldResponse]:
    """
    Fixture containing a list of precision farming fields.
    :param db: database fixture
    :param farms: the farms to link fields to
    """
    field_service = FieldService(db)

    precision_fields = [
        field_service.create_field_by_field_type(
            field_request=FieldRequest(
                number=1,
                size=Decimal(15.0),
                owned=True,
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
                owned=True,
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
                owned=True,
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

    return precision_fields


@pytest.fixture
def base_game_field(base_game_fields, db) -> Field:
    """
    Fixture for a single base game field.
    :param db: database fixture.
    :param base_game_fields: base fields fixture.
    """
    field_repository = FieldRepository(db)
    return field_repository.get_by_id(base_game_fields[0].id)


@pytest.fixture
def precision_farming_field(precision_farming_fields, db) -> Field:
    """
    Fixture for a single precision farming field.
    :param db: database fixture.
    :param precision_farming_fields: precision farming fields fixture.
    """
    field_repository = FieldRepository(db)
    return field_repository.get_by_id(precision_farming_fields[0].id)


@pytest.fixture
def tasks(farm, db):
    """
    Pytest tasks fixture
    """
    task_service = TaskService(db)
    task_service.create_task("new task data 1", completed=False, farm_id=farm.id)
    task_service.create_task("new task data 2", completed=True, farm_id=farm.id)
    task_service.create_task("new task data 3", completed=False, farm_id=farm.id)
    return farm.tasks
