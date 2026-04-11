"""
Security Service Module
"""

import datetime
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from src.svc.envsvc import AppEnv
from src.svc.errsvc import InsufficientRoleError, InvalidTokenError


class SecSvc:
    """
    Singleton Security Service
    Centralized access to security-related configuration and utilities.
    """

    _instance = None
    _settings: AppEnv | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecSvc, cls).__new__(cls)
            cls._instance._init_settings()
        return cls._instance

    def _init_settings(self) -> None:
        """
        Initialize settings once per application lifecycle.
        """
        if self._settings is None:
            self._settings = AppEnv()

    def get_appenv(self) -> AppEnv:
        """
        Returns application environment configuration.
        """
        return self._settings

    def hash_password(self, plain: str) -> str:
        """Method to hash password"""
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

    def verify_password(self, plain: str, hashed: str) -> bool:
        """Method to verify password"""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    def create_access_token(
        self,
        user_id: int,
        role: str,
        expires_seconds: Optional[int] = None,
    ) -> str:
        """Method to create access token"""
        expire = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(
            seconds=expires_seconds
            or self._settings.access_token_expire_seconds
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }
        return jwt.encode(
            payload,
            self._settings.secret_key,
            algorithm=self._settings.algorithm,
        )

    def decode_access_token(self, token: str) -> dict:
        """
        Decodes and validates a JWT token.
        Raises JWTError if token is invalid or expired —
        caller is responsible for handling it.
        """
        return jwt.decode(
            token,
            self._settings.secret_key,
            algorithms=[self._settings.algorithm],
        )


class AuthSvc:

    def __init__(self):
        self.sec_svc = SecSvc()

    def decode_token(self, token: str) -> dict:
        """
        Decode and validate a JWT. Returns the payload dict.
        Raises TokenInvalidError on any failure.
        """
        try:
            return self.sec_svc.decode_access_token(token)
        except JWTError as e:
            raise InvalidTokenError() from e

    def auth(self, token: str, *allowed_roles: str) -> dict:
        """
        Verify token AND assert the caller's role is in allowed_roles.

        Returns the full payload so you can extract user_id etc. in one call:
            payload = auth.require_role(token, "admin", "moderator")
            user_id = int(payload["sub"])

        Raises:
            TokenInvalidError     – bad / expired token
            InsufficientRoleError – token valid but role not permitted
        """
        payload = self.decode_token(token)
        role = payload.get("role")
        if role not in allowed_roles:
            raise InsufficientRoleError()
        return payload
