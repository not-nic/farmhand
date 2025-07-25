"""
Crop Repository containing crop database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from typing import Optional

from sqlalchemy.orm import Session

from src.api.core.db.models.crops import Crop
from src.api.core.repositories import Repository


class CropRepository(Repository[Crop]):
    """
    Crop Repository for interaction with the DB
    """

    def __init__(self, db: Session):
        super().__init__(db, Crop)

    def get_by_type(self, type: str) -> Optional[Crop]:
        """
        Get a crop by its type / plaintext name e.g. Wheat.
        :param type: the type of crop.
        :return: the crop object.
        """
        return self.db.query(Crop).filter(Crop.type == type).first()
