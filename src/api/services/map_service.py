"""
Map Service Module currently used for manually scraping map data
when new maps are released.
"""
from sqlalchemy.orm import Session

from src.api.constants import MapFilters
from src.api.core.repositories import MapRepository
from src.api.services.modhub_service import ModHubService
from src.api.core.logger import logger
from src.api.utils import parse_version


class MapService:
    """
    Map Service used for getting map information from the ModHub
    and creating map entries in the database.
    """

    def __init__(self, db: Session):
        self.mod_hub_service = ModHubService()
        self.map_repository = MapRepository(db)

    async def get_maps(self):
        """
        Function to get all the maps from the Farming Simulator ModHub
        and store their information into the Maps table of the database.
        :return:
        """
        map_ids = []

        # iterate over all the map filters and make requests to each category's mod page.
        for map_filter in MapFilters:
            pages = self.mod_hub_service.get_pages(map_filter)

            for page in pages:
                mod_ids = self.mod_hub_service.scrape_mods(category=map_filter, page=page)
                map_ids.extend(mod_ids)

        # iterate over all the collected mod ids and scrape the mod page data.
        for mod_id in map_ids:
            mod_detail = self.mod_hub_service.scrape_mod(mod_id)

            mod_map = self.map_repository.get_by_id(mod_id)

            if not mod_map:
                logger.info(f"Creating Map {mod_detail.name} ({mod_detail.id})")
                self.map_repository.create(
                    id=mod_detail.id,
                    name=mod_detail.name,
                    category=mod_detail.category,
                    author=mod_detail.author,
                    release_date=mod_detail.release_date,
                    version=mod_detail.version
                )
            else:
                if self.is_newer_version(current_version=mod_map.version, new_version=mod_detail.version):
                    logger.info(f"Updating Map {mod_detail.name} ({mod_detail.id}) "
                                f"from version {mod_map.version} to {mod_detail.version}")
                    self.map_repository.update(mod_map.id, version=mod_detail.version)
                else:
                    logger.info(f"Map: {mod_detail.name} ({mod_detail.id}) is already up-to-date "
                                f"(version {mod_map.version}).")

    @staticmethod
    def is_newer_version(current_version: str, new_version: str) -> bool:
        """
        Compare two version strings like '1.0.0.0'.
        Return True if new_version is greater.
        :param new_version: the new map version from ModHub.
        :param current_version: the current map version in the db
        """
        return parse_version(new_version) > parse_version(current_version)
