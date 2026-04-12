"""User repository"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.user import User, UserRole
from src.schemas.user import UserCreate
from src.svc.dbsvc import DbSvc
from src.svc.secsvc import SecSvc


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
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """get user by id"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_instructors(self, club_id: int) -> list[User]:
        """get all active instructors for a club"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(User).where(
                    User.club_id == club_id,
                    User.role == UserRole.INSTRUCTOR,
                    User.is_active.is_(True),
                )
            )
            return list(result.scalars().all())

    async def get_all(self, club_id: int) -> list[User]:
        """get all users for a club"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(User).where(User.club_id == club_id)
            )
            return list(result.scalars().all())

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
        async with self.db_svc.get_sessionmaker()() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
