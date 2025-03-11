from fastapi import APIRouter, BackgroundTasks, status, Depends

from src.api.deps import is_service_user
from src.api.services.map_service import MapService
from src.api.services.modhub_service import ModHubService

router = APIRouter(prefix="/scrape", tags=["scraper"])


@router.get(
    "/{id}",
    dependencies=[Depends(is_service_user)],
    status_code=status.HTTP_202_ACCEPTED
)
async def scrape_data(id: int, background_tasks: BackgroundTasks):
    mod_hub_service = ModHubService()
    background_tasks.add_task(mod_hub_service.scrape_mod, mod_id=id)

    return {"detail": "Started Scraping Task"}


@router.get(
    "/",
    dependencies=[Depends(is_service_user)],
    status_code=status.HTTP_202_ACCEPTED
)
async def scrape_maps(background_tasks: BackgroundTasks):
    """
    :param background_tasks:
    :return:
    """
    map_service = MapService()
    background_tasks.add_task(map_service.get_maps)
    return {"detail": "Started Scraping all maps"}
