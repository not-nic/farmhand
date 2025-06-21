"""
Field Crop Repository containing field crop database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from sqlalchemy.orm import Session

from src.api.core.db.models import FieldCrop
from src.api.core.repositories import Repository


class FieldCropRepository(Repository[FieldCrop]):
    """
    FieldCrop Repository for interaction with the DB
    """
    def __init__(self, db: Session):
        super().__init__(db, FieldCrop)