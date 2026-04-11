from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.user import User
from src.svc.dbsvc import DbSvc


class UserRepository:
    """
    User data access layer
    """

    def __init__(self):
        self.db_svc = DbSvc()

    async def get_session(self) -> AsyncSession:
        return self.db_svc.get_sessionmaker()()

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
