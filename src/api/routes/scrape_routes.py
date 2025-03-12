from fastapi import APIRouter, BackgroundTasks, status, Depends

from src.api.deps import is_service_user
from src.api.services.map_service import MapService
from src.api.services.modhub_service import ModHubService

router = APIRouter(prefix="/scrape", tags=["scraper"])


@router.get("/{id}", dependencies=[Depends(is_service_user)], status_code=status.HTTP_202_ACCEPTED)
async def scrape_data(id: int, background_tasks: BackgroundTasks):
    """
    Function to manually trigger scraping of an individual mod by its mod_id.
    :param id: the mod_id in the ModHub URL
    :param background_tasks: The background task to add the scrape function too.
    :return: (202) Accepted and a message that the scraping has been started in the background.
    """
    mod_hub_service = ModHubService()
    background_tasks.add_task(mod_hub_service.scrape_mod, mod_id=id)
    return {"detail": "Started Scraping Task"}


@router.get("/", dependencies=[Depends(is_service_user)], status_code=status.HTTP_202_ACCEPTED)
async def scrape_maps(background_tasks: BackgroundTasks):
    """
    Function to manually trigger the scraping of maps from the Farming Simulator ModHub website.
    :param background_tasks: The background task to add the scrape function too.
    :return: (202) Accepted and a message that the scraping has been started in the background.
    """
    map_service = MapService()
    background_tasks.add_task(map_service.get_maps)
    return {"detail": "Started Scraping all maps"}
