from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


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
