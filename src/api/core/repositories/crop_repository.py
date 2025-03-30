"""
Crop Repository containing crop database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from typing import Optional, TYPE_CHECKING
from src.api.core.repositories.base_repository import Repository

if TYPE_CHECKING:
    from src.api.core.db.models.crops import Crop


class CropRepository(Repository):
    """
    User Repository for interaction with the DB
    """

    __abstract__ = True

    @classmethod
    def get_by_type(cls: "Crop", type: str) -> Optional["Crop"]:
        """
        Get a crop by its type / plaintext name e.g. Wheat.
        :param type: the type of crop.
        :return: the crop object.
        """
        return cls.get_session().query(cls).filter(cls.type == type).first()
