"""
Module for creating the FastAPI router
"""
from fastapi import APIRouter
from src.api.routes import auth_routes, user_routes, farm_routes

api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(farm_routes.router)

