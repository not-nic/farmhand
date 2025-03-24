"""
Logging Module for the farmhand application
"""

import logging

from src.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))

# Passlib raises an error about not being able to find an attribute in bcrypt.
logging.getLogger('passlib').setLevel(logging.ERROR)

logger.addHandler(log_handler)


