"""Maintenance window repository"""

import datetime
import logging
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.maintenance_window import MaintenanceWindow
from src.schemas.maintenance import MaintenanceWindowCreate
from src.svc.dbsvc import DbSvc

logger = logging.getLogger(__name__)


class MaintenanceRepository:
    """Maintenance window data access layer"""

    def __init__(self):
        self.db_svc = DbSvc()

    async def get_all(self, club_id: int, page: int = 1, limit: int = 20) -> tuple[list[MaintenanceWindow], int]:
        """Get all maintenance windows for a club with pagination"""
        async with self.db_svc.get_sessionmaker()() as session:
            count_stmt = select(func.count()).select_from(MaintenanceWindow).where(MaintenanceWindow.club_id == club_id)
            total = await session.scalar(count_stmt)

            stmt = select(MaintenanceWindow).where(
                MaintenanceWindow.club_id == club_id
            ).offset((page - 1) * limit).limit(limit)
            
            result = await session.execute(stmt)
            return list(result.scalars().all()), total or 0

    async def get_by_aircraft(
        self, aircraft_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[MaintenanceWindow], int]:
        """Get maintenance windows for a specific aircraft with pagination"""
        async with self.db_svc.get_sessionmaker()() as session:
            count_stmt = select(func.count()).select_from(MaintenanceWindow).where(MaintenanceWindow.aircraft_id == aircraft_id)
            total = await session.scalar(count_stmt)

            stmt = select(MaintenanceWindow).where(
                MaintenanceWindow.aircraft_id == aircraft_id
            ).offset((page - 1) * limit).limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all()), total or 0

    async def get_by_id(self, window_id: int) -> Optional[MaintenanceWindow]:
        """Get a maintenance window by id"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(MaintenanceWindow).where(
                    MaintenanceWindow.id == window_id
                )
            )
            return result.scalar_one_or_none()

    async def create(
        self, club_id: int, data: MaintenanceWindowCreate
    ) -> MaintenanceWindow:
        """Create a maintenance window"""
        async with self.db_svc.get_sessionmaker()() as session:
            window = MaintenanceWindow(club_id=club_id, **data.model_dump())
            session.add(window)
            await session.commit()
            await session.refresh(window)
            logger.info("Maintenance window created: %s", window.id)
            return window

    async def delete(self, window_id: int) -> bool:
        """Delete a maintenance window, returns True if found and deleted"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(MaintenanceWindow).where(
                    MaintenanceWindow.id == window_id
                )
            )
            window = result.scalar_one_or_none()
            if not window:
                return False
            await session.delete(window)
            await session.commit()
            logger.info("Maintenance window deleted: %s", window_id)
            return True
