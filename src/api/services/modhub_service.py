import requests

from typing import Optional
from fastapi import status
from bs4 import BeautifulSoup, Tag
from requests import HTTPError

from src.api.constants import URLs
from src.api.core.models import Mod
from src.api.utils import logger


class ModHubService:
    """
    Module to scrape the Farming Simulator ModHub and get information about Mods.
    """

    def scrape_mod(self, mod_id: int) -> Mod:
        """
        Scrape a mod page and return a pydantic model of the mod details
        :param mod_id: the id of the mod to scrape
        :return: (Mod) Pydantic model or raise value error.
        """
        url = self.create_mod_url(mod_id=mod_id)
        response = requests.get(url)

        if response.status_code != status.HTTP_200_OK:
            logger.warning(
                f"Unable to connect to the ModHub - got status code: {response.status_code}"
            )
            raise HTTPError(f"Request failed with status code: {response.status_code}")

        page_contents = BeautifulSoup(response.content, "html.parser")

        mod_name = page_contents.find("h2", class_="column title-label").get_text(strip=True)
        mod_info = page_contents.find("div", class_="table table-game-info")

        if mod_info:
            mod_details = self.get_mod_details(mod_info)
            mod_details["id"] = mod_id
            mod_details["name"] = mod_name

            logger.info(f"Found mod information for {mod_name} ({mod_id})")

            mod_detail = Mod(**mod_details)
            return mod_detail
        else:
            logger.warning(
                f"Mod ID: {mod_id} - Unable to scrape mod information as 'mod-info div' was not found."
            )
            raise ValueError(
                f"Mod ID: {mod_id} - Unable to scrape mod information as 'mod-info div' was not found."
            )

    def scrape_mods(self, category: Optional[str] = None) -> list:
        """
        Scrape the 'mods' pages and get the ids for each mod displayed
        :param category: the category to get mods for i.e. MapFilters constants
        :return: a list of mod_ids scraped from the page.
        """
        url = self.create_mods_url(category_filter=category if category else "")

        response = requests.get(url)

        if response.status_code != status.HTTP_200_OK:
            logger.warning(
                f"Unable to connect to the ModHub - got status code: {response.status_code}"
            )
            raise HTTPError(f"Request failed with status code: {response.status_code}")

        page_contents = BeautifulSoup(response.content, "html.parser")
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
                    mod_ids.append(self.get_mod_id(mod_item))

        return mod_ids

    @staticmethod
    def create_mods_url(
        category_filter: Optional[str] = None,
        page: Optional[int] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        create a URL to scrape a mod by its category or without.
        :param page: the page to scrape (should be handled as an increment)
        :param category_filter: the category to scrape i.e. FarmsEurope
        :param title: The Farming Sim game version
        :return: a string of the created url
        """
        return (
            f"{URLs.BASE_MODS_URL}"
            + (f"?filter={category_filter}" if category_filter else "")
            + (f"&title={title}" if title else "")
            + (f"&page={page}" if page else "")
        )

    @staticmethod
    def create_mod_url(mod_id: int, title: Optional[str] = None) -> str:
        """
        create a ModHub url for a specific mod that can be scraped.
        :param mod_id: the id of the mod to request
        :param title: the Farming Sim game version
        :return: a string of the created url
        """
        return f"{URLs.BASE_MOD_URL}?mod_id={mod_id}" + (f"&title={title}" if title else "")

    @staticmethod
    def get_mod_details(mod_info: Tag) -> dict:
        """
        Function to get the stats about a mod author, release date, size, etc
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

    @staticmethod
    def get_mod_id(mod_item: Tag) -> int:
        """
        Get the id for the mod based on the href of the 'MORE_INFO' button.
        :param mod_item: the current mod item
        :return: (int) the id of the mod
        """
        more_info_tag = mod_item.find("a", class_="button-buy")
        if more_info_tag:
            href = more_info_tag.get("href", "")
            if "mod_id=" in href:
                mod_id = href.split("mod_id=")[1].split("&")[0]
                return int(mod_id)
