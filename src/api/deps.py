from fastapi import Request, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from src.api.core.models import User
from src.api.core.repositories import sessions

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/v1/login"
)

def get_current_user(request: Request) -> dict:
    """
    dependency to get the current user by their session token
    :param request: the incoming request object.
    :return: the current logged-in user object.
    """
    session_token = request.cookies.get("session")

    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session token missing or invalid")

    session_data = sessions.get(session_token)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")

    username = session_data["username"]
    user = User.get_by_username(username)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "username": user.username,
        "email_address": user.email_address,
        "name": user.name,
        "created_at": user.created_at,
        "session": session_token
    }