"""Module for session management"""

import logging

from src.repositories.users import UserRepository
from src.schemas.auth import LoginRequest, TokenResponse
from src.svc.errsvc import InvalidCredentialsError
from src.svc.secsvc import SecSvc

logger = logging.getLogger(__name__)


class SeshSvc:
    """Class for managing session"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.sec_svc = SecSvc()

    async def login(self, req: LoginRequest) -> TokenResponse:
        """login method"""
        user = await self.user_repo.get_by_email(req.email)

        if not user or not self.sec_svc.verify_password(
            req.password, user.hashed_password
        ):
            raise InvalidCredentialsError()

        token = self.sec_svc.create_access_token(
            user_id=user.id,
            role=user.role,
        )
        logger.info(
            "User with user_id: %s and role: %s login successful",
            user.id,
            user.role.value,
        )

        return TokenResponse(
            access_token=token,
            expires_in=self.sec_svc.get_appenv().access_token_expire_seconds,
        )
