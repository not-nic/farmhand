import string
import random


def generate_session_token():
    """
    Util function to generate a session token.
    :return: a randomised 128 character string.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=128))