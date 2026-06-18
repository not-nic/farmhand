"""
Python module containing a farm service for class for creating and managing farms.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from src.api.constants import FarmTypes, Difficulty
from src.api.core.db.models import Farm, User
from src.api.core.repositories import FarmRepository
from src.api.services.data_service import DataApiService
from src.api.utils import possessive
from tests.fixtures import farms


class FarmService:
    """
    Python class for the Farm Service for managing player farms.
    """
    def __init__(self, db: Session) -> None:
        self.db = db
        self.farm_repository = FarmRepository(self.db)
        self.data_service = DataApiService()

    async def create_farm(
            self,
            map_id: int,
            farm_type: FarmTypes,
            difficulty: Difficulty,
            user: User
    ) -> Farm:
        """
        Create a farm by providing a farm type (base or pf) and a map_id
        from the ModHub.
        :param map_id: The id of the map from the ModHub
        :param farm_type: The type of farm to create (base, pf)
        :param difficulty: The economic difficulty of the Farm (Easy, Medium, Hard)
        :param user: A User object.
        :returns: The created farm.
        """
        map_obj = await self.data_service.get_map_by_id(map_id)

        if not map_obj:
            raise ValueError("Map not found.")

        farm = self.farm_repository.create(
            name=f"{map_obj.name} Farm",
            description=f"{possessive(user.username)} new farm on {map_obj.name}-{map_obj.version}",
            map_name=map_obj.name,
            owner_id=user.id,
            map_id=map_obj.id,
            farm_type=farm_type,
            difficulty=difficulty,
        )

        return farm

    def update_farm(
            self,
            farm: Farm,
            name: str | None = None,
            description: str | None = None,
            difficulty: Difficulty | None = None,
    ) -> None:
        """
        Update a given farm's name, description, or difficulty.
        :param farm: The farm to update.
        :param name: A new name.
        :param description: A new description.
        :param difficulty: A new difficulty.
        """
        update_data = {}

        if name is not None:
            update_data["name"] = name

        if description is not None:
            update_data["description"] = description

        if difficulty is not None:
            update_data["difficulty"] = difficulty

        if not update_data:
            return

        self.farm_repository.update(farm, **update_data)

    def get_by_id(self, farm_id: UUID) -> Farm | None:
        """
        Get a farm by its ID.
        :param farm_id: the ID of the farm/
        :return: (Farm) Returns a farm object if it exists.
        """
        return self.farm_repository.get_by_id(farm_id)

    def delete_farm(self, farm: Farm) -> None:
        """
        Delete a given farm.
        :param farm: The farm to delete.
        """
        self.farm_repository.delete(farm)

    @staticmethod
    def get_farms(current_user: User) -> list[Farm]:
        """
        Get all farms for a given user.
        :param current_user: A user object.
        :return: A list of farms.
        """
        return current_user.farms
