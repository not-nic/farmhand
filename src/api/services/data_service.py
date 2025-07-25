"""
Python module containing the 'DataApiService' for communicating
with the farmhand data API.
"""
from typing import Optional

import httpx
from fastapi import status
from httpx import ConnectError, RequestError, Response

from src.api.core.logger import logger
from src.api.exceptions.farmhand_data_api_exceptions import ServiceUnavailableError
from src.config import settings


class DataApiService:
    """
    Class containing the Data API Service which is used to communicate
    with the farmhand-data-api, to get information from the game files or modhub.
    """
    def __init__(self, url: Optional[str] = None):
        self.data_api_url = settings.DATA_API_URL or url

    async def get_map_by_id(self, map_id: int) -> Optional[dict]:
        """
        Get a map by its ID from the data-api.
        :param map_id:
        """
        logger.info(f"[Data API Service]: retrieving map from data-api with ID: {map_id}")

        response = await self._make_request("GET", f"/maps/{map_id}")
        if response.status_code == status.HTTP_200_OK:
            return response.json()
        return None

    async def _make_request(self, method: str, endpoint: str, params: Optional[dict] = None) -> Response:
        """
        Reusable HTTP request method using httpx.
        :param method: HTTP method as a string (e.g., "GET").
        :param endpoint: Endpoint to hit (e.g., "/maps/1").
        :param params: Optional query parameters.
        :return: JSON response as dict.
        """
        url = f"{self.data_api_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                return await client.request(method, url, params=params)
            except ConnectError as exc:
                logger.error(f"[Data API Service]: Connection failed to {url}: {exc}")
                raise ServiceUnavailableError("farmhand-data-api is unreachable.") from exc
            except RequestError as exc:
                logger.error(f"[Data API Service]: Request error for {url}: {exc}")
                raise ServiceUnavailableError("Request to farmhand-data-api failed.") from exc
