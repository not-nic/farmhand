import logging
import string
import random

from src.api.constants import FieldTypes, FarmTypes
from src.api.core.db_models import Farm
from src.api.core.models import FieldRequest
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


def is_base_game_field(field_request: FieldRequest, current_farm: Farm) -> bool:
    """
    Check if the request is for creating a base game field on a base game farm.
    """
    return field_request.field_type == FieldTypes.BASE_FIELD and current_farm.farm_type == FarmTypes.BASE


def is_precision_farming_field(field_request: FieldRequest, current_farm: Farm) -> bool:
    """
    check if the request is creating a precision farming field
    """
    return (field_request.field_type == FieldTypes.PRECISION_FARMING_FIELD and
            current_farm.farm_type == FarmTypes.PRECISION_FARMING)
