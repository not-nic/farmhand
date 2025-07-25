"""
Module for testing the Farmhand Security class.
"""

import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from src.api.constants import AuthTypes
from src.api.core.db.models import User
from src.api.core.repositories import UserRepository
from src.api.core.schema.users import TokenModel
from src.api.core.security import Security
from src.config import settings


class TestSecurity:
    def test_get_user_by_default_auth_type(self, db, unit_test_user: User):
        """
        Test that when passed a TokenModel containing a 'default' AuthType claim
        the user is retrieved by their id and returned.
        :param db: database fixture
        :param unit_test_user: Create unit test user fixture
        """
        expected_token = TokenModel(
            id=unit_test_user.id,
            auth_type=AuthTypes.DEFAULT,
            exp=datetime.now(timezone.utc) + settings.JWT_TOKEN_EXPIRATION_TIME,
            iat=datetime.now(timezone.utc),
        )

        user_repository = UserRepository(db)
        expected_user = Security.get_user_by_auth_type(
            token=expected_token, user_repository=user_repository
        )

        assert expected_user == unit_test_user

    def test_get_user_by_github_auth_type(self, db, github_user: User):
        """
        Test that when passed a TokenModel containing a 'GitHub' AuthType claim
        the user is retrieved by their GitHub id and returned.
        :param db: Create database fixture.
        :param github_user: GitHub Unit Testing user.
        """
        expected_token = TokenModel(
            id=github_user.github_id,
            auth_type=AuthTypes.GITHUB,
            exp=datetime.now(timezone.utc) + settings.GITHUB_TOKEN_EXPIRATION_TIME,
            iat=datetime.now(timezone.utc),
        )

        user_repository = UserRepository(db)
        expected_user = Security.get_user_by_auth_type(
            token=expected_token, user_repository=user_repository
        )
        assert expected_user == github_user

    def test_security_encode_and_decode_jwt(self):
        """
        Test that a valid TokenModel is correctly encoded into a JWT token
        and correctly decoded into a JWT token.
        """
        token_payload = TokenModel(
            id=12345,
            auth_type=AuthTypes.GITHUB,
            exp=datetime.now(timezone.utc) + settings.GITHUB_TOKEN_EXPIRATION_TIME,
            iat=datetime.now(timezone.utc),
        )

        encoded_token = Security.encode_jwt(token_payload)
        decoded_payload = Security.decode_jwt(encoded_token)

        assert decoded_payload.id == token_payload.id
        assert decoded_payload.auth_type == token_payload.auth_type
        assert decoded_payload.expires_at is not None
        assert decoded_payload.issued_at is not None

    def test_encode_jwt_failure_invalid_payload(self):
        """
        Test that encoding fails when an invalid payload is provided.
        """
        with pytest.raises(AttributeError):
            Security.encode_jwt(None)

    def test_decode_jwt_raises_expired_signature_error(self):
        """
        Test that when given an expired token the Security.decode_jwt raises
        a ExpiredSignatureError exception.
        """

        token = TokenModel(
            id=12345,
            auth_type=AuthTypes.DEFAULT,
            exp=datetime.now(timezone.utc) + timedelta(milliseconds=5),
            iat=datetime.now(timezone.utc),
        )

        with pytest.raises(jwt.ExpiredSignatureError):
            expired_token = Security.encode_jwt(token)
            time.sleep(0.05)
            Security.decode_jwt(expired_token)

    def test_decode_jwt_raises_invalid_token_error(self):
        """
        Test that when given an invalid token the Security.decode_jwt raises
        a InvalidTokenError exception.
        """
        with pytest.raises(jwt.InvalidTokenError):
            Security.decode_jwt("invalid.jwt.token")
