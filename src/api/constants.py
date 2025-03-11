from strenum import StrEnum


class URLs(StrEnum):
    BASE_MODS_URL = "https://www.farming-simulator.com/mods.php"
    BASE_MOD_URL = "https://www.farming-simulator.com/mod.php"


class MapFilters(StrEnum):
    EUROPEAN_MAPS = "mapEurope"
    NORTH_AMERICAN_MAPS = "mapNorthAmerica"
    SOUTH_AMERICAN_MAPS = "mapSouthAmerica"
    OTHER_MAPS = "mapOthers"


class GameVersions(StrEnum):
    FS_2025 = "fs2025"
    FS_2022 = "fs2022"
