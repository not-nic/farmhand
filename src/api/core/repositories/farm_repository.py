"""
Farm Repository containing farm database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from sqlalchemy.orm import Session

from src.api.core.db.models import Farm
from src.api.core.repositories import Repository


class FarmRepository(Repository[Farm]):
    """
    Farm Repository for interaction with the DB
    """
    def __init__(self, db: Session):
        super().__init__(db, Farm)