"""
Module for initialisation scripts (fixtures) to be run
on the start-up of the application.
"""

from src.api.core.db_models import User
from src.api.core.security import Security
from src.api.services.crop_service import CropService
from src.api.logger import logger
from src.config import settings


class Fixtures:
    @staticmethod
    def create_service_user() -> User:
        """
        Python fixture to create or update a service-user on startup of the application.
        If the service user already exists, update the username, email, and password.
        :return: (User) the created or updated user.
        """

        logger.info("Creating service user...")

        user_data = {
            "username": settings.SERVICE_USER_USERNAME,
            "email_address": settings.SERVICE_USER_EMAIL,
            "password": Security.get_password_hash(settings.SERVICE_USER_PASSWORD),
            "name": "service-user",
        }

        service_user = User.get_by_username(username=settings.SERVICE_USER_USERNAME)

        if not service_user:
            service_user = User.create(**user_data)
            logger.info(f"Service user created - {service_user.email_address}")
        else:
            logger.info("Service user already exists, updating values if changed.")
            service_user.update(id=service_user.id, **user_data)

        return service_user

    @staticmethod
    async def create_crop_data() -> None:
        """
        Python Fixture for creating crop data on application startup if it does not exist.
        """
        crop_service = CropService()
        await crop_service.load_crops()
