import datetime
import pytest

from requests import HTTPError
from fastapi import status

from src.api.core.models import Mod
from src.api.services.modhub_service import ModHubService


class TestModHubService:
    def test_scrape_mock_mod(self, mock_mod_hub_page):
        """
        Test that when scraping a modhub mod a Mod pydantic model is returned
        and is populated with the correct values.
        :param mock_mod_hub_page: the mock modhub page to scrape.
        """

        mock_mod_hub_page(file_name="mod.html", status_code=status.HTTP_200_OK)

        mod_hub_service = ModHubService()
        result = mod_hub_service.scrape_mod(mod_id=12345)

        assert isinstance(result, Mod)
        assert result.game == "Farming Simulator 25"
        assert result.manufacturer == "Lizard"
        assert result.category == "Yield Improvements - Fertilizer Spreaders"
        assert result.author == "Zimov"
        assert result.size == 4.38
        assert result.version == "1.0.0.0"
        assert result.release_date == datetime.date(year=2025, month=3, day=12)
        assert result.platform == ["PC/MAC", "PS5", "XBS"]

    def test_scrape_mod_page_with_no_mod(self, mock_mod_hub_page):
        """
        Test that a ValueError is raised if the mod_item does not exist.
        :param mock_mod_hub_page: the mock modhub page to scrape.
        """
        mock_mod_hub_page(file_name="no_mod.html", status_code=status.HTTP_200_OK)
        with pytest.raises(
            ValueError,
            match="Mod ID: 12345 - Unable to scrape mod information as 'mod-info div' was not found.",
        ):
            mod_hub_service = ModHubService()
            mod_hub_service.scrape_mod(mod_id=12345)

    def test_scrape_mod_raises_http_error(self, mock_mod_hub_page):
        """
        Test that if the modhub is down, an HTTP error is raised.
        :param mock_mod_hub_page: the mock modhub page to scrape.
        """
        mock_mod_hub_page(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        with pytest.raises(HTTPError, match="Request failed with status code: 503"):
            mod_hub_service = ModHubService()
            mod_hub_service.scrape_mod(mod_id=12345)

    def test_scrape_mock_mods(self, mock_mod_hub_page):
        """
        Test scraping a mocked mods page from the modhub and asserting that
        all mod_ids (ints) are returned.
        :param mock_mod_hub_page: the mock modhub page to scrape.
        """
        mock_mod_hub_page(file_name="mods.html", status_code=status.HTTP_200_OK)
        mod_hub_service = ModHubService()
        result = mod_hub_service.scrape_mods()

        assert isinstance(result, list)

        for mod_id in result:
            isinstance(mod_id, int)

    def test_scrape_mods_raises_http_error(self, mock_mod_hub_page):
        """
        Test that if the modhub is down, an HTTP error is raised.
        :param mock_mod_hub_page: the mock modhub page to scrape.
        """
        mock_mod_hub_page(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        with pytest.raises(HTTPError, match="Request failed with status code: 503"):
            mod_hub_service = ModHubService()
            mod_hub_service.scrape_mods()
