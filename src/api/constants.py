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
    Fertilizer states for a base game field which map to percentage
    of yield improvement:
        0% - 0% yield improvement
        50% - 22.5% yield improvement
        100% - 45% yield improvement
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


class Difficulty(Enum):
    """
    Enum for Farming Simulator difficulty levels.
    """
    EASY = 3.0
    MEDIUM = 1.5
    HARD = 1


class FSData(Enum):
    """
    An assortment of static values taken from farming simulator to make
    calculations i.e. seed price, fertilizer price etc.
    All values should be * 1000 to get their value per 1000l.
    """

    # Base Costs
    BASE_SEED_PRICE = 1.26
    BASE_SOLID_FERTILIZER_PRICE = 1.92
    BASE_LIQUID_FERTILIZER_PRICE = 1.60

    # Farming Simulator Percentage increases to yield
    LIMED = 15
    PLOWED = 15
    WEEDS = 20
    MULCHED = 2.5
    ROLLED = 2.5

    # pH levels for each soil type
    LOAM_PH_LEVELS = [(6.750, 15), (6.500, 10), (6.250, 5)]
    SANDY_LOAM_PH_LEVELS = [(6.500, 15), (6.250, 10), (6.000, 5)]
    SILTY_CLAY_PH_LEVELS = [(7.000, 15), (6.750, 10), (6.500, 5)]
    LOAMY_SAND_PH_LEVELS = [(6.000, 15), (5.750, 10), (5.500, 5)]

    # Fertilizer, Lime and Herbicide rates in litres per second
    SOLID_FERTILIZER_RATE = 0.0060
    LIQUID_FERTILIZER_RATE = 0.0081
    MANURE_RATE = 0.4000
    LIQUID_MANURE_RATE = 0.4000
    DIGESTATE_RATE = 0.4000
    LIME_RATE = 0.0900
    HERBICIDE_RATE = 0.0081

    # Precision Farming Solid Fertilizer Density
    SOLID_FERTILIZER_DENSITY = 0.8


class FertilizerTypes(StrEnum):
    """
    Types of Fertilizer in Farming Simulator
    """
    SOLID = "solid"
    LIQUID = "liquid"
    MANURE = "manure"
    SLURRY = "slurry"
    DIGESTATE = "digestate"


class FertilizerEffect(Enum):
    """
    Fertilizer states for a base game field which map to percentage
    of yield improvement:
        NOT_FERTILIZED - 0% yield improvement
        HALF_FERTILIZED - 22.5% yield improvement
        FULLY_FERTILIZED - 45% yield improvement
    """

    NOT_FERTILIZED = 0
    HALF_FERTILIZED = 22.5
    FULLY_FERTILIZED = 45
