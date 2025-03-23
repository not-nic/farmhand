from fastapi import APIRouter, Depends, status, HTTPException
from src.api.deps import get_current_user
from src.api.core.models import UserCreate
from src.api.core.db_models import User
from src.api.core.security import Security

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_user_info(current_user: User = Depends(get_current_user)) -> dict:
    """
    (Temp) Get the information of a current logged-in user.
    :param current_user:
    :return:
    """
    return {
        "email": current_user.email_address,
        "username": current_user.username,
        "name": current_user.name,
        "created_at": current_user.created_at
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate) -> dict:
    """
    Create a new user in the service
    :param user_create: create user pydantic model
    :return: 201 Created message if successful.
    """
    exists_by_username = User.get_by_username(user_create.username)
    exists_by_email = User.get_by_email(user_create.email_address)

    if exists_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    if exists_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user_create.password = Security.get_password_hash(user_create.password)
    User.create(**user_create.model_dump())

    return {"message": "Account created successfully"}
