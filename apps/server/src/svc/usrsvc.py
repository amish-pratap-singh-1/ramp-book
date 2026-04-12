"""User service module"""

import logging
from typing import Optional

from src.entities.user import User
from src.repositories.users import UserRepository
from src.schemas.user import UserCreate
from src.svc.errsvc import UserNotFoundError, DuplicateEntryError

logger = logging.getLogger(__name__)


class UsrSvc:
    """Class for managing user related business logic"""

    def __init__(self):
        self.user_repo = UserRepository()

    async def get_me(self, user_id: int) -> User:
        """Get current user info"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def list_instructors(self, user_id: int, page: int, limit: int) -> tuple[list[User], int]:
        """List active instructors for the user's club"""
        user = await self.get_me(user_id)
        return await self.user_repo.get_instructors(user.club_id, page, limit)

    async def list_users(self, admin_id: int, page: int, limit: int) -> tuple[list[User], int]:
        """List all users for the admin's club"""
        admin = await self.get_me(admin_id)
        return await self.user_repo.get_all(admin.club_id, page, limit)

    async def create_user(self, admin_id: int, data: UserCreate) -> User:
        """Create a new user in the admin's club"""
        admin = await self.get_me(admin_id)
        
        # Check if email is already taken
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise DuplicateEntryError("Email already registered")
            
        return await self.user_repo.create(admin.club_id, data)
