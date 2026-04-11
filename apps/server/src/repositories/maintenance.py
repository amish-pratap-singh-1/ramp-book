"""Maintenance window repository"""

import datetime
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.maintenance_window import MaintenanceWindow
from src.schemas.maintenance import MaintenanceWindowCreate
from src.svc.dbsvc import DbSvc


class MaintenanceRepository:
    """Maintenance window data access layer"""

    def __init__(self):
        self.db_svc = DbSvc()

    async def get_all(self, club_id: int) -> list[MaintenanceWindow]:
        """Get all maintenance windows for a club"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(MaintenanceWindow).where(
                    MaintenanceWindow.club_id == club_id
                )
            )
            return list(result.scalars().all())

    async def get_by_aircraft(
        self, aircraft_id: int
    ) -> list[MaintenanceWindow]:
        """Get maintenance windows for a specific aircraft"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(MaintenanceWindow).where(
                    MaintenanceWindow.aircraft_id == aircraft_id
                )
            )
            return list(result.scalars().all())

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
            return True
