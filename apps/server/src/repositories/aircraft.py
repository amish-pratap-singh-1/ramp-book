"""Aircraft repository"""

import datetime
import logging
from typing import Optional

from sqlalchemy import and_, func, select

from src.entities.aircraft import Aircraft
from src.entities.maintenance_window import MaintenanceWindow
from src.entities.reservation import Reservation, ReservationStatus
from src.schemas.aircraft import (AircraftCreate, AircraftScheduleItem,
                                  AircraftUpdate)
from src.svc.dbsvc import DbSvc

logger = logging.getLogger(__name__)


class AircraftRepository:
    """Aircraft data access layer"""

    def __init__(self):
        self.db_svc = DbSvc()

    async def get_all(
        self, club_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Aircraft], int]:
        """Get all aircraft for a club with pagination"""
        async with self.db_svc.get_sessionmaker()() as session:
            count_stmt = (
                select(func.count())
                .select_from(Aircraft)
                .where(Aircraft.club_id == club_id)
            )
            total = await session.scalar(count_stmt)

            stmt = (
                select(Aircraft)
                .where(Aircraft.club_id == club_id)
                .offset((page - 1) * limit)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all()), total or 0

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
            logger.info("Aircraft created: %s", aircraft.id)
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
            logger.info("Aircraft updated: %s", aircraft_id)
            return aircraft

    async def is_available(
        self,
        aircraft_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        exclude_reservation_id: Optional[int] = None,
    ) -> bool:
        """Check if aircraft has no conflicting reservations
        or maintenance windows"""
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

    async def get_schedule(
        self, aircraft_id: int
    ) -> list[AircraftScheduleItem]:
        """Fetch all busy blocks (reservations and maintenance)
        for an aircraft"""
        schedule = []
        async with self.db_svc.get_sessionmaker()() as session:
            # 1. Fetch future confirmed reservations
            res_query = select(Reservation).where(
                and_(
                    Reservation.aircraft_id == aircraft_id,
                    Reservation.status == ReservationStatus.CONFIRMED,
                    Reservation.end_time
                    > datetime.datetime.now(datetime.timezone.utc),
                )
            )
            reservations = await session.execute(res_query)
            for r in reservations.scalars().all():
                schedule.append(
                    AircraftScheduleItem(
                        id=r.id,
                        start_time=r.start_time.isoformat(),
                        end_time=r.end_time.isoformat(),
                        type="reservation",
                    )
                )

            # 2. Fetch future maintenance
            maint_query = select(MaintenanceWindow).where(
                and_(
                    MaintenanceWindow.aircraft_id == aircraft_id,
                    MaintenanceWindow.end_time
                    > datetime.datetime.now(datetime.timezone.utc),
                )
            )
            maintenance = await session.execute(maint_query)
            for m in maintenance.scalars().all():
                schedule.append(
                    AircraftScheduleItem(
                        id=m.id,
                        start_time=m.start_time.isoformat(),
                        end_time=m.end_time.isoformat(),
                        type="maintenance",
                    )
                )

        return schedule
