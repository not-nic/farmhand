"""
Security module for handling various secure functions such as JWT encoding / decoding,
OAuth configuration and password hashing.
"""

from typing import Optional

import bcrypt
import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordBearer

from src.api.constants import AuthTypes
from src.api.core.db.models.users import User
from src.api.core.repositories import UserRepository
from src.api.core.schema.users import TokenModel
from src.config import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

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
        Verify the password hash of an incoming login.
        :param plain_password: Plaintext password sent in request
        :param hashed_password: hashed password stored in DB
        :return: boolean if the password matches hash.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Create a hash for a plaintext password.
        :param password: Plaintext password
        :return: hashed password
        """
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    @staticmethod
    def get_user_by_auth_type(token: TokenModel, user_repository: UserRepository) -> Optional[User]:
        """
        Get a user based on the auth claim in the JWT Token.
        :param token: The JWT token values
        :param user_repository: the User Repository instance
        :return: (User) if it exists for the matching auth type.
        """
        if token.auth_type == AuthTypes.DEFAULT:
            return user_repository.get_by_id(token.id)

        if token.auth_type == AuthTypes.GITHUB:
            return user_repository.get_by_github_id(token.id)

        return None

    @staticmethod
    def encode_jwt(payload: TokenModel) -> str:
        """
        Encode a JWT token with a TokenModel payload.
        :param payload: (TokenModel) of the data to encode
        :return: (str) JWT token of encoded data.
        """
        return jwt.encode(
            payload=payload.model_dump(mode="json", by_alias=True),
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_jwt(token: str) -> TokenModel:
        """
        Decode a JWT token back into a TokenModel.
        :param token: (str) Encoded JWT token.
        :return: (TokenModel) of the decoded JWT data.
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return TokenModel(**payload)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise
