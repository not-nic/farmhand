from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    Request model for logging into the service.
    """

    username: str
    password: str
