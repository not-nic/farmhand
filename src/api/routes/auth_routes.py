import jwt

from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from fastapi.responses import RedirectResponse
import datetime

from src.api.deps import get_current_user
from src.api.core.models import LoginRequest, GithubUser
from src.api.core.db_models import User
from src.api.core.security import Security, github
from src.api.utils import generate_session_token, logger
from src.api.core.repositories import sessions
from src.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest, response: Response) -> dict:
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
    sessions[session_token] = {"username": user.username, "created_at": datetime.datetime.now(datetime.UTC)}

    response.set_cookie(key="session", value=session_token, httponly=True, secure=True)

    return {"message": "login successful"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: dict = Depends(get_current_user)) -> Response:
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


@router.get("/github")
async def login(request: Request):
    return await github.authorize_redirect(request, settings.GITHUB_OAUTH_CALLBACK_URL)


@router.get("/github/callback")
async def auth(request: Request):
    token = await github.authorize_access_token(request)
    response = await github.get("https://api.github.com/user", token=token)

    github_user = GithubUser(**response.json())

    logger.info(f"[Github Auth]: Logged in as {github_user.username}")

    user = User.get_by_github_id(github_user.id)

    # Create user if it does not exist
    if not user:
        logger.info(f"[Github Auth]: User {github_user.username} does not exist, creating new user...")
        User.create(
            github_id=github_user.id,
            email=github_user.email,
            username=github_user.username,
            name=github_user.name
        )

    expiry_time = datetime.datetime.now(datetime.UTC) + settings.JWT_EXPIRATION_TIME

    payload = {
        "id": github_user.id,
        "username": github_user.username,
        "email": github_user.email,
        "name": github_user.name,
        "exp": expiry_time
    }

    session_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    response = RedirectResponse(url="/docs")
    response.set_cookie(key="farmhand_user", value=session_token, httponly=True, secure=True)
    return response

