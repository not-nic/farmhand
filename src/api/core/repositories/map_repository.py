"""
Map Repository containing map database interactions.
see: base_repository.py to see the base repository to inherit from.
"""

from sqlalchemy.orm import Session

from src.api.core.db.models import Map
from src.api.core.repositories import Repository


class MapRepository(Repository[Map]):
    """
    Map Repository for interaction with the DB
    """

    def __init__(self, db: Session):
        super().__init__(db, Map)
