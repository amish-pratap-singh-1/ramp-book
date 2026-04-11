"""
Security Service Module
"""
import datetime
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.svc.envsvc import AppEnv


class SecSvc:
    """
    Singleton Security Service
    Centralized access to security-related configuration and utilities.
    """

    _instance = None
    _settings: AppEnv | None = None
    _pwd_context: CryptContext | None = None

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
            self._pwd_context = CryptContext(
                schemes=["bcrypt"], deprecated="auto")

    def get_appenv(self) -> AppEnv:
        """
        Returns application environment configuration.
        """
        return self._settings

    def hash_password(self, plain: str) -> str:
        return self._pwd_context.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self._pwd_context.verify(plain, hashed)

    def create_access_token(
        self,
        user_id: int,
        role: str,
        expires_seconds: Optional[int] = None,
    ) -> str:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=expires_seconds or self._settings.access_token_expire_seconds
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
            algorithm=self._settings.algorithm
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
            algorithms=[self._settings.algorithm]
        )

    def get_user_id_from_token(self, token: str) -> int:
        """
        Convenience method — decode token and return user_id as int.
        Raises JWTError if invalid.
        """
        payload = self.decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise JWTError("Token missing subject")
        return int(sub)

    def get_role_from_token(self, token: str) -> str:
        """
        Convenience method — decode token and return role string.
        Raises JWTError if invalid.
        """
        payload = self.decode_access_token(token)
        role = payload.get("role")
        if role is None:
            raise JWTError("Token missing role")
        return role
