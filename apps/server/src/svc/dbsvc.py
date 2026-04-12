"""
Database Service Module
"""

from typing import AsyncGenerator

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.svc.errsvc import DatabaseError, DuplicateEntryError
from src.svc.secsvc import SecSvc


class DbSvc:
    """
    Singleton Database Service
    """

    _instance = None
    _engine = None
    _sessionmaker = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DbSvc, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self) -> None:
        """
        Initialize DB engine and sessionmaker once.
        """
        settings = SecSvc().get_appenv()
        url = settings.database_url

        self._engine = create_async_engine(
            url,
            pool_pre_ping=True,
        )

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def get_sessionmaker(self):
        """
        Returns session factory.
        """
        return self._sessionmaker

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency-style DB session.
        """
        async with self._sessionmaker() as session:
            yield session

    @staticmethod
    def handle_db_error(e: Exception) -> None:
        """
        Centralized database error handler.
        Maps SQLAlchemy/driver errors to AppError subclasses.
        """
        if isinstance(e, IntegrityError):
            # SQLAlchemy wraps the driver's exception in e.orig
            orig = getattr(e, "orig", None)

            # Check for unique violation (Postgres SQLSTATE 23505)
            # Check by instance type OR by SQLSTATE code for robustness
            if (
                isinstance(orig, UniqueViolationError)
                or getattr(orig, "sqlstate", None) == "23505"
            ):
                raise DuplicateEntryError(
                    detail="A record with this value already exists"
                ) from e

        if isinstance(e, SQLAlchemyError):
            raise DatabaseError(detail=str(e)) from e

        # If it's already an AppError or something else, re-raise it
        raise e
