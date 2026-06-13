"""
API Routes for Authentication using either username and password
or GitHub OAuth.

This module defines the authentication routes for logging in users with their
username and password or via GitHub OAuth.

Routes:
    - POST /auth/login: Log in using a username and password.
    - GET /auth/github: Redirect to GitHub OAuth for authentication.
    - GET /auth/github/callback: Callback from GitHub to authenticate the user and create a JWT token.
    - POST /auth/logout: Log out and delete the JWT token cookie.

Dependencies:
    - SessionDep: Database session object
    - CurrentUser: Fetches the current authenticated user.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from src.api.constants import AuthTypes
from src.api.core.db.models.users import User
from src.api.core.dependencies import SessionDep, get_current_user
from src.api.core.logger import logger
from src.api.core.repositories import UserRepository
from src.api.core.schema.login import LoginRequest
from src.api.core.schema.users import GithubUser, TokenModel
from src.api.core.security import Security, github
from src.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest, db: SessionDep, response: Response) -> dict:
    """
    Endpoint for logging into the service with a username and password
    :param login_request: login request pydantic model
    :param db: database session.
    :param response: return a message and set a session token cookie.
    :return:
    """
    user_repository = UserRepository(db)
    user: User = user_repository.get_by_username(login_request.username)

    if not user or not Security.verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect"
        )

    payload = TokenModel(
        id=user.id,
        exp=datetime.now(UTC) + settings.JWT_TOKEN_EXPIRATION_TIME,
        iat=datetime.now(UTC),
    )

    session_token = Security.encode_jwt(payload)
    response.set_cookie(key="farmhand_user", value=session_token, httponly=True, secure=True)

    return {"message": "login successful"}


@router.get("/github", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def github_login(request: Request) -> Response:
    """
    Authorise GitHub account and redirect to the call back
    :param request: The user request object.
    :return: (redirect) to the GitHub authentication page.
    """
    return await github.authorize_redirect(request, settings.GITHUB_OAUTH_CALLBACK_URL)


@router.get("/github/callback", status_code=status.HTTP_302_FOUND)
async def authenticate_github(request: Request, db: SessionDep) -> Response:
    """
    Authenticate the user with a GitHub access token and create a user if
    they do not exist. Then encode the GitHub id into a JWT to be used on
     requests to the service.

    :param request: the users request
    :param db: database session
    :return: (jwt) session token containing the users GitHub id.
    """
    user_repository = UserRepository(db)

    token = await github.authorize_access_token(request)
    response = await github.get("https://api.github.com/user", token=token)

    github_user = GithubUser(**response.json())
    user = user_repository.get_by_github_id(github_user.id)

    # Create user if it does not exist
    if not user:
        logger.info("[Github Auth]: User does not exist, creating a new user")
        user_repository.create(
            github_id=github_user.id,
            email_address=github_user.email,
            username=github_user.username,
            name=github_user.name,
        )

    payload = TokenModel(
        id=github_user.id,
        auth_type=AuthTypes.GITHUB,
        exp=datetime.now(UTC) + settings.GITHUB_TOKEN_EXPIRATION_TIME,
        iat=datetime.now(UTC),
    )

    session_token = Security.encode_jwt(payload)

    response = RedirectResponse(url=settings.FRONTEND_REDIRECT_URL)
    response.set_cookie(key="farmhand_user", value=session_token, httponly=True, secure=True)
    return response


@router.post(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)]
)
async def logout() -> Response:
    """
    Endpoint to log out and delete the JWT token cookie.
    :return: 204 No content after the user has logged out.
    """
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("farmhand_user")

    return response
