"""User repository"""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.user import User, UserRole
from src.schemas.user import UserCreate
from src.svc.dbsvc import DbSvc
from src.svc.errsvc import DatabaseError
from src.svc.secsvc import SecSvc

logger = logging.getLogger(__name__)


class UserRepository:
    """
    User data access layer
    """

    def __init__(self):
        self.db_svc = DbSvc()
        self.sec_svc = SecSvc()

    async def get_session(self) -> AsyncSession:
        """get db session"""
        return self.db_svc.get_sessionmaker()()

    async def get_by_email(self, email: str) -> Optional[User]:
        """get user by email"""
        try:
            async with self.db_svc.get_sessionmaker()() as session:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=str(e)) from e

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """get user by id"""
        try:
            async with self.db_svc.get_sessionmaker()() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=str(e)) from e

    async def get_instructors(
        self, club_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[User], int]:
        """get all active instructors for a club with pagination"""
        try:
            async with self.db_svc.get_sessionmaker()() as session:
                # Count total
                count_stmt = (
                    select(func.count())  # pylint: disable=not-callable
                    .select_from(User)
                    .where(
                        User.club_id == club_id,
                        User.role == UserRole.INSTRUCTOR,
                        User.is_active.is_(True),
                    )
                )
                total = await session.scalar(count_stmt)

                # Get items
                stmt = (
                    select(User)
                    .where(
                        User.club_id == club_id,
                        User.role == UserRole.INSTRUCTOR,
                        User.is_active.is_(True),
                    )
                    .order_by(User.created_at.desc())
                    .offset((page - 1) * limit)
                    .limit(limit)
                )

                result = await session.execute(stmt)
                return list(result.scalars().all()), total or 0
        except SQLAlchemyError as e:
            raise DatabaseError(detail=str(e)) from e

    async def get_all(
        self, club_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[User], int]:
        """get all users for a club with pagination"""
        try:
            async with self.db_svc.get_sessionmaker()() as session:
                # Count total
                count_stmt = (
                    select(func.count())  # pylint: disable=not-callable
                    .select_from(User)
                    .where(User.club_id == club_id)
                )
                total = await session.scalar(count_stmt)

                # Get items
                stmt = (
                    select(User)
                    .where(User.club_id == club_id)
                    .order_by(User.created_at.desc())
                    .offset((page - 1) * limit)
                    .limit(limit)
                )

                result = await session.execute(stmt)
                return list(result.scalars().all()), total or 0
        except SQLAlchemyError as e:
            raise DatabaseError(detail=str(e)) from e

    async def create(self, club_id: int, data: UserCreate) -> User:
        """create a new user"""
        hashed_pw = self.sec_svc.hash_password(data.password)
        user = User(
            club_id=club_id,
            email=data.email,
            hashed_password=hashed_pw,
            full_name=data.full_name,
            role=data.role,
            certificate=data.certificate,
            ratings=data.ratings,
        )
        try:
            async with self.db_svc.get_sessionmaker()() as session:
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info("User created: %s", user.id)
                return user
        except SQLAlchemyError as e:
            raise DatabaseError(detail=str(e)) from e
