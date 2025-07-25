"""
API Routes for User Management.

This module defines the API routes for managing user-related actions.
It allows fetching the current logged-in user's information and creating new users.

Routes:
    - GET /users/me: Get the information of the current logged-in user.
    - POST /users: Create a new user with a username, email, and password.

Dependencies:
    - get_current_user: Fetches the current authenticated user.
"""

from fastapi import APIRouter, HTTPException, status

from src.api.core.dependencies import CurrentUser, SessionDep
from src.api.core.repositories import UserRepository
from src.api.core.schema.users import UserCreate
from src.api.core.security import Security

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_user_info(current_user: CurrentUser) -> dict:
    """
    (Temp) Get the information of a current logged-in user.
    :param current_user: current user dependency
    :return: (dict) of the current user details
    """
    # TODO: Make this response return a pydantic object
    return {
        "email": current_user.email_address,
        "username": current_user.username,
        "name": current_user.name,
        "created_at": current_user.created_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: SessionDep) -> dict:
    """
    Create a new user in the service
    :param user_create: create user pydantic model
    :param db: database session dependency
    :return: 201 Created message if successful.
    """
    user_repository = UserRepository(db)

    exists_by_username = user_repository.get_by_username(user_create.username)
    exists_by_email = user_repository.get_by_email(user_create.email_address)

    if exists_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    if exists_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user_create.password = Security.get_password_hash(user_create.password)
    user_repository.create(**user_create.model_dump())

    return {"message": "Account created successfully"}
