"""
Module for the FastAPI routes and the routers
each set of routes should be appended too.
"""

from fastapi import APIRouter, Depends

from src.api.core.dependencies import get_current_user, get_farm
from src.api.routes import (
    auth_routes,
    user_routes,
    farm_routes,
    scrape_routes,
    field_routes,
    crop_routes,
    metrics_routes,
    tasks_routes,
)

api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(user_routes.router)

field_routes.router.include_router(
    router=metrics_routes.router, dependencies=[Depends(get_current_user), Depends(get_farm)]
)

field_routes.router.include_router(
    router=crop_routes.router, dependencies=[Depends(get_current_user), Depends(get_farm)]
)

api_router.include_router(field_routes.router)
api_router.include_router(tasks_routes.router)
api_router.include_router(farm_routes.router)
api_router.include_router(scrape_routes.router)
