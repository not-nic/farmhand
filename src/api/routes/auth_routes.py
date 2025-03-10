from fastapi import APIRouter, HTTPException, Depends, status, Response
from datetime import datetime

from src.api.deps import get_current_user
from src.api.core.models import LoginRequest
from src.api.core.db_models import User
from src.api.core.security import Security
from src.api.utils import generate_session_token
from src.api.core.repositories import sessions

router = APIRouter(tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest, response: Response):
    """
    Endpoint for logging into the service with a username and password
    :param login_request: login request pydantic model
    :param response: return a message and set a session token cookie.
    :return:
    """
    user = User.get_by_username(login_request.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect"
        )

    if not Security.verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect"
        )

    session_token = generate_session_token()
    sessions[session_token] = {"username": user.username, "created_at": datetime.utcnow()}

    response.set_cookie(key="session", value=session_token, httponly=True, secure=True)

    return {"message": "login successful"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Endpoint to log out and delete the session cookie.
    :param current_user: the current logged-in user.
    :return: 204 No content after the user has logged out.
    """
    session_token = current_user["session"]

    if session_token in sessions:
        sessions.pop(session_token)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("session")

    return response
