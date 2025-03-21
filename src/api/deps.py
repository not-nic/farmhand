from typing import Annotated, Optional
from uuid import UUID

from fastapi import Request, HTTPException, status, Depends, Path
from fastapi.security import OAuth2PasswordBearer

from src.api.core.db_models import User, Farm, Field
from src.api.core.repositories import sessions
from src.api.services.field_service import FieldService
from src.config import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_current_user(request: Request) -> User:
    """
    dependency to get the current user by their session token
    :param request: the incoming request object.
    :return: the current logged-in user object.
    """
    session_token = request.cookies.get("session")

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session token missing or invalid"
        )

    session_data = sessions.get(session_token)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token"
        )

    username = session_data["username"]
    user = User.get_by_username(username)

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
            detail="You do not have permission to access this resource."
        )
    return True


def get_users_farm(
        id: Annotated[UUID, Path(title="The ID of the farm to get")],
        current_user: CurrentUser
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


CurrentFarm = Annotated[Farm, Depends(get_users_farm)]


def get_field(
    field_id: Annotated[UUID, Path(title="The ID of the field to get")],
) -> Optional[Field]:
    """
    dependency to get the current field by its ID or return
    a 404 if it doesn't exist.
    :param field_id: the id of the field to get
    """
    try:
        return FieldService.get_field(field_id=field_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")


CurrentField = Annotated[Field, Depends(get_field)]
