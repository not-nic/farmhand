import json
import pprint

import requests

from typing import Optional
from bs4 import BeautifulSoup, Tag

from src.api.constants import URLs, MapFilters
from src.api.core.db_models import Map
from src.api.core.models import Mod
from src.api.utils import logger


class ModHubService:
    # def __init__(self):
    # mods_url = "https://www.farming-simulator.com/mods.php?title=fs2025&filter=mapEurope&page=0"
    # mod_url = "https://www.farming-simulator.com/mod.php?mod_id=313458&title=fs2025"
    # title = "fs2025", "fs2022"
    # filters = "mapEurope", "mapNorthAmerica", "mapSouthAmerica", "mapOthers"

    async def scrape_all(self):
        mod_ids = await self.scrape_mod_pages()

        for mod_id in mod_ids:
            await self.scrape(mod_id)

        logger.info(f"Collected Mod Ids: {mod_ids}")

    # generic function to scrape data about a mod
    async def scrape(self, mod_id: int):
        """
        Scrape a mod page and return a pydantic model of the mod details
        :param mod_id: the id of the mod to scrape
        :return: (Mod) Pydantic model or raise value error.
        """
        url = self.create_mod_url(mod_id=mod_id)
        response = requests.get(url)

        page_contents = BeautifulSoup(response.content, "html.parser")

        mod_name = page_contents.find("h2", class_="column title-label").get_text(strip=True)
        mod_info = page_contents.find("div", class_="table table-game-info")

        if mod_info:
            mod_details = self.get_mod_details(mod_info)
            mod_details["id"] = mod_id
            mod_details["name"] = mod_name

            logger.info(f"Mod Name: {mod_name}")
            logger.info(f"Mod Info: {mod_details}")

            mod_detail = Mod(**mod_details)

            logger.info(mod_detail)

            # temp save "map" to database
            self.create_map_entry(mod_detail)

            return mod_detail
        else:
            raise ValueError("Unable to extract data from mod page")

    # Scrape map function (something to add to the maps table)
    # Maybe handle this somewhere else in a map service, keep this class generic.
    @staticmethod
    def create_map_entry(mod_detail: Mod):
        Map.create(
            id=mod_detail.id,
            name=mod_detail.name,
            category=mod_detail.category,
            author=mod_detail.author,
            release_date=mod_detail.release_date,
        )

    # Function to scrape the mod pages, to get a collection of mods and ids.
    async def scrape_mod_pages(self) -> list:
        url = self.create_mods_url(category_filter=MapFilters.EUROPEAN_MAPS)
        # url = self.create_mods_url()

        response = requests.get(url)
        page_contents = BeautifulSoup(response.content, "html.parser")

        # Get all rows that contain mods from a ModHub page
        rows = page_contents.find_all("div", class_="row")

        mod_ids = []

        # iterate over each row and get the container for each mod
        for row in rows:
            mod_item_containers = row.find_all("div", class_="medium-6 large-3 columns")

            # loop over each container and get the 'mod-item' div and get the id for the
            # mod page from the 'MORE INFO' tag.
            for container in mod_item_containers:
                mod_item = container.find("div", class_="mod-item")

                if mod_item:
                    more_info_tag = mod_item.find("a", class_="button-buy")
                    if more_info_tag:
                        href = more_info_tag.get("href", "")
                        if "mod_id=" in href:
                            mod_id = href.split("mod_id=")[1].split("&")[0]
                            mod_ids.append(mod_id)

        return mod_ids

    # util methods:

    # create mods_url with filters, pages & title
    @staticmethod
    def create_mods_url(
        category_filter: Optional[str] = None,
        page: Optional[int] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        create a URL to scrape a mod by its category or without.
        :param page:
        :param category_filter:
        :param title: the Farming Sim game version
        :return: a string of the created url
        """
        return (
            f"{URLs.BASE_MODS_URL}"
            + (f"?filter={category_filter}" if category_filter else "")
            + (f"&title={title}" if title else "")
            + (f"&page={page}" if page else "")
        )

    # create mod_url with mod_id & title (optional, if you have ID not needed)
    @staticmethod
    def create_mod_url(mod_id: int, title: Optional[str] = None) -> str:
        """
        create a ModHub url for a specific mod that can be scraped.
        :param mod_id: the id of the mod to request
        :param title: the Farming Sim game version
        :return: a string of the created url
        """
        return f"{URLs.BASE_MOD_URL}?mod_id={mod_id}" + (f"&title={title}" if title else "")

    # method to get the stats about a mod author, release date, size, etc
    @staticmethod
    def get_mod_details(mod_info: Tag) -> dict:
        """
        Get the details of a mod from the table on the mod website
        :param mod_info: HTML Element of the Table
        :return: a dict of key and values e.g. author, mod_size, release date, etc.
        """
        info = {}

        for row in mod_info.find_all("div", class_="table-row"):
            cells = row.find_all("div", class_="table-cell")

            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                info[key] = value

        return info
