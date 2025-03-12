from src.api.constants import MapFilters
from src.api.core.db_models import Map
from src.api.services.modhub_service import ModHubService


class MapService:

    def __init__(self):
        self.mod_hub_service = ModHubService()

    async def get_maps(self):
        """
        Function to get all the maps from the Farming Simulator ModHub
        and store their information into the Maps table of the database.
        :return:
        """
        map_ids = []

        # iterate over all the map filters and make requests to each category's mod page.
        for map_filter in MapFilters:
            mod_ids = self.mod_hub_service.scrape_mods(category=map_filter)
            map_ids.extend(mod_ids)

        # iterate over all the collected mod ids and scrape the mod page data.
        for mod_id in map_ids:
            mod_detail = self.mod_hub_service.scrape_mod(mod_id)

            Map.create(
                id=mod_detail.id,
                name=mod_detail.name,
                category=mod_detail.category,
                author=mod_detail.author,
                release_date=mod_detail.release_date,
            )
