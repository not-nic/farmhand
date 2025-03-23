from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth

from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
