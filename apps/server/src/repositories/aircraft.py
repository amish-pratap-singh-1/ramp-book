"""Aircraft repository"""

import datetime
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.aircraft import Aircraft
from src.entities.maintenance_window import MaintenanceWindow
from src.entities.reservation import Reservation, ReservationStatus
from src.schemas.aircraft import AircraftCreate, AircraftUpdate
from src.svc.dbsvc import DbSvc


class AircraftRepository:
    """Aircraft data access layer"""

    def __init__(self):
        self.db_svc = DbSvc()

    async def get_all(self, club_id: int) -> list[Aircraft]:
        """Get all aircraft for a club"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Aircraft).where(Aircraft.club_id == club_id)
            )
            return list(result.scalars().all())

    async def get_by_id(self, aircraft_id: int) -> Optional[Aircraft]:
        """Get aircraft by id"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Aircraft).where(Aircraft.id == aircraft_id)
            )
            return result.scalar_one_or_none()

    async def create(self, club_id: int, data: AircraftCreate) -> Aircraft:
        """Create a new aircraft"""
        async with self.db_svc.get_sessionmaker()() as session:
            aircraft = Aircraft(club_id=club_id, **data.model_dump())
            session.add(aircraft)
            await session.commit()
            await session.refresh(aircraft)
            return aircraft

    async def update(
        self, aircraft_id: int, data: AircraftUpdate
    ) -> Optional[Aircraft]:
        """Update aircraft fields"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Aircraft).where(Aircraft.id == aircraft_id)
            )
            aircraft = result.scalar_one_or_none()
            if not aircraft:
                return None
            for field, value in data.model_dump(exclude_none=True).items():
                setattr(aircraft, field, value)
            await session.commit()
            await session.refresh(aircraft)
            return aircraft

    async def is_available(
        self,
        aircraft_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        exclude_reservation_id: Optional[int] = None,
    ) -> bool:
        """Check if aircraft has no conflicting reservations or maintenance windows"""
        async with self.db_svc.get_sessionmaker()() as session:
            # Check active reservations overlap
            res_query = select(Reservation).where(
                and_(
                    Reservation.aircraft_id == aircraft_id,
                    Reservation.status == ReservationStatus.CONFIRMED,
                    Reservation.start_time < end,
                    Reservation.end_time > start,
                )
            )
            if exclude_reservation_id:
                res_query = res_query.where(
                    Reservation.id != exclude_reservation_id
                )
            res_result = await session.execute(res_query)
            if res_result.scalar_one_or_none():
                return False

            # Check maintenance windows overlap
            maint_result = await session.execute(
                select(MaintenanceWindow).where(
                    and_(
                        MaintenanceWindow.aircraft_id == aircraft_id,
                        MaintenanceWindow.start_time < end,
                        MaintenanceWindow.end_time > start,
                    )
                )
            )
            if maint_result.scalar_one_or_none():
                return False

            return True
