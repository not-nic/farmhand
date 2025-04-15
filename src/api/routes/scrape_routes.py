"""
API Routes for Scraping Data from ModHub.

This module defines the API routes for manually triggering scraping operations.
It allows the 'Service User' to scrape data from the ModHub.

Routes:
    - GET /scrape/{id}: Manually trigger scraping of an individual mod by its mod_id.
    - GET /scrape/maps: Manually trigger scraping of all maps from the ModHub website.

Dependencies:
    - is_service_user: Ensures that the request is coming from a service user.
"""

from fastapi import APIRouter, BackgroundTasks, status, Depends

from src.api.core.dependencies import is_service_user
from src.api.services.map_service import MapService
from src.api.services.modhub_service import ModHubService

router = APIRouter(prefix="/scrape", tags=["Scraper"])


@router.get("/mods/{id}", dependencies=[Depends(is_service_user)], status_code=status.HTTP_202_ACCEPTED)
async def scrape_mod(id: int, background_tasks: BackgroundTasks) -> dict:
    """
    Function to manually trigger scraping of an individual mod by its mod_id.
    :param id: the mod_id in the ModHub URL
    :param background_tasks: The background task to add the scrape function too.
    :return: (202) Accepted and a message that the scraping has been started in the background.
    """
    mod_hub_service = ModHubService()
    background_tasks.add_task(mod_hub_service.scrape_mod, mod_id=id)
    return {"detail": f"scraping mod: {id}"}


@router.get("/maps", dependencies=[Depends(is_service_user)], status_code=status.HTTP_202_ACCEPTED)
async def scrape_maps(background_tasks: BackgroundTasks) -> dict:
    """
    Function to manually trigger the scraping of maps from the Farming Simulator ModHub website.
    :param background_tasks: The background task to add the scrape function too.
    :return: (202) Accepted and a message that the scraping has been started in the background.
    """
    map_service = MapService()
    background_tasks.add_task(map_service.get_maps)
    return {
        "detail": "Started scraping all maps from ModHub."
    }
