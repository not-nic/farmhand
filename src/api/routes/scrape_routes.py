from fastapi import APIRouter, BackgroundTasks, status

from src.api.services.modhub_service import ModHubService

router = APIRouter(prefix="/scrape", tags=["scraper"])


@router.get("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def scrape_data(id: int, background_tasks: BackgroundTasks):
    mod_hub_service = ModHubService()
    background_tasks.add_task(mod_hub_service.scrape, mod_id=id)

    return {"detail": "Started Scraping Task"}


@router.get("/", status_code=status.HTTP_202_ACCEPTED)
async def scrape_all_data(background_tasks: BackgroundTasks):
    mod_hub_service = ModHubService()
    background_tasks.add_task(mod_hub_service.scrape_all)

    return {"detail": "Started Scraping all Task"}
