import logging
import string
import random

from src.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(settings.LOG_FORMATTER, datefmt="%Y-%m-%d %H:%M:%S"))

# Passlib raises an error about not being able to find an attribute in bcrypt.
logging.getLogger('passlib').setLevel(logging.ERROR)

logger.addHandler(log_handler)


def generate_session_token() -> str:
    """
    Util function to generate a session token.
    :return: a randomised 128 character string.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=128))


