"""
Collection of Enums used within the Farmhand service.
"""

from enum import Enum

from strenum import StrEnum


class AuthTypes(StrEnum):
    """
    Constants for authentication types, i.e. default (username/password)
    and oauth e.g. GitHub.
    """

    DEFAULT = "default"
    GITHUB = "github"


class URLs(StrEnum):
    """
    ModHub URLs
     - mods_url: The page that displays multiple mods
     - mod_url: a page for an individual mod
    """

    BASE_MODS_URL = "https://www.farming-simulator.com/mods.php"
    BASE_MOD_URL = "https://www.farming-simulator.com/mod.php"


class MapFilters(StrEnum):
    """
    All map filters for the modhub, used to scrape all maps.
    """

    EUROPEAN_MAPS = "mapEurope"
    NORTH_AMERICAN_MAPS = "mapNorthAmerica"
    SOUTH_AMERICAN_MAPS = "mapSouthAmerica"
    OTHER_MAPS = "mapOthers"


class GameVersions(StrEnum):
    """
    Versions of the supported and used for scraping.
    """

    FS_2025 = "fs2025"
    FS_2022 = "fs2022"


class FarmTypes(StrEnum):
    """
    Types of farms a user can create, either a 'base' (game) farm
    or 'precision farming' farm for different fields.
    """

    BASE = "base"
    PRECISION_FARMING = "precision_farming"


class FieldTypes(StrEnum):
    """
    Types of fields that can be created in the DB.
    """

    PRECISION_FARMING_FIELD = "precision_field"
    BASE_FIELD = "base_field"


class FertilizerStates(Enum):
    """
    Fertilizer states used in the 'Base Game' fields
    either 0%, 50% or 100% fertilized.
    """

    ZER0_PERCENT = 0
    FIFTY_PERCENT = 50
    ONE_HUNDRED_PERCENT = 100


class WeedStates(Enum):
    """
    Weed states used in both fields, as each weed type
    has a different impact on yield.
    """

    NO_WEEDS = 0
    SMALL_WEEDS = 1
    MEDIUM_WEEDS = 2
    LARGE_WEEDS = 3
    SPRAYED_WEEDS = 4


class SoilTypes(StrEnum):
    """
    Types of Soil used in precision farming fields.
    """

    SANDY_LOAM = "sandy loam"
    LOAMY_SAND = "loamy sand"
    SILTY_CLAY = "silty clay"
    LOAM = "loam"
