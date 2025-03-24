"""
Security module for handling various secure functions such as JWT encoding / decoding,
OAuth configuration and password hashing.
"""

import jwt

from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth

from src.api.constants import AuthTypes
from src.api.core.db_models import User
from src.api.core.models import TokenModel
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

oauth = OAuth()

oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    client_kwargs={"scope": "user:email"},
)

github = oauth.github


class Security:
    """
    Class for security functions such as password hashing and comparison.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        verify the password hash of an incoming login.
        :param plain_password: plaintext password sent in request
        :param hashed_password: hashed password stored in DB
        :return: boolean if password matches hash.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        create a hash for a plaintext password.
        :param password: plaintext password
        :return: hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def get_user_by_auth_type(token: TokenModel) -> Optional[User]:
        """
        Get a user based on the auth claim in the JWT Token.
        :param token: the JWT token values
        :return: (User) if it exists for the matching auth type.
        """

        if token.auth_type == AuthTypes.DEFAULT:
            return User.get(token.id)

        if token.auth_type == AuthTypes.GITHUB:
            return User.get_by_github_id(token.id)

    @staticmethod
    def encode_jwt(payload: TokenModel) -> str:
        """
        Encode a JWT token with a TokenModel payload
        :param payload: (TokenModel) of the data to encode
        :return: (str) JWT token of encoded data.
        """
        return jwt.encode(
            payload=payload.model_dump(mode="json", by_alias=True),
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_jwt(token: str) -> TokenModel:
        """
        Decode a JWT token back into a TokenModel.
        :param token: (str) Encoded JWT token.
        :return: (TokenModel) of the decoded JWT data.
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return TokenModel(**payload)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise
