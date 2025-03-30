"""
Module for FastAPI Dependencies that need to be called / injected before methods can be called.
"""

from typing import Annotated, Optional
from uuid import UUID

import jwt
from fastapi import HTTPException, Depends, Path
from starlette import status
from starlette.requests import Request

from src.api.core.db.models.fields import Field
from src.api.core.db.models.farms import Farm
from src.api.core.db.models.users import User
from src.api.core.security import Security
from src.api.services.field_service import FieldService
from src.config import settings


async def get_current_user(request: Request) -> User:
    """
    Function to get the current user based on the JWT token stored in the user's
    session.
    :param request: the users request object
    :return: (User) the user associated with the request.
    """
    session_token = request.cookies.get("farmhand_user")

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token"
        )

    try:
        token = Security.decode_jwt(session_token)
        user = Security.get_user_by_auth_type(token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def is_service_user(current_user: CurrentUser) -> bool:
    """
    (Temp) dependency to check if the current logged-in user
    is the service user to trigger scrape commands.
    :param current_user: the current logged-in user
    :return: (Bool) if the current user is the service-user
    """

    if (
        current_user.username != settings.SERVICE_USER_USERNAME
        or current_user.email_address != settings.SERVICE_USER_EMAIL
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )
    return True


ServiceUser = Annotated[bool, Depends(is_service_user)]


def get_farm(
    id: Annotated[UUID, Path(title="The ID of the farm to get")], current_user: CurrentUser
) -> Farm:
    """
    Get the farm for the current logged-in user
    :param id: the id of the farm to get
    :param current_user: the current user of the farm
    :return: the requested Farm
    """
    farm = Farm.get(id)

    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    if farm.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{current_user.username} does not own this farm.",
        )

    return farm


CurrentFarm = Annotated[Farm, Depends(get_farm)]


def get_field(
        current_farm: CurrentFarm,
        field_id: Annotated[UUID, Path(title="The ID of the field to get")],
) -> Optional[Field]:
    """
    dependency to get the current field by its ID or return
    a 404 if it doesn't exist.
    :param current_farm: the farm requested with the field.
    :param field_id: the id of the field to get
    """
    try:
        return FieldService.get_field(field_id=field_id, farm_id=current_farm.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this field; it belongs to a different farm.",
        )


CurrentField = Annotated[Field, Depends(get_field)]
