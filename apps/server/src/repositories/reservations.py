"""Reservations repository"""

import datetime
import logging
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from src.entities.aircraft import Aircraft
from src.entities.reservation import Reservation, ReservationStatus
from src.schemas.reservation import ReservationCreate, ReservationUpdate
from src.svc.dbsvc import DbSvc

logger = logging.getLogger(__name__)


class ReservationRepository:
    """Reservation data access layer"""

    def __init__(self):
        self.db_svc = DbSvc()

    def _with_relations(self):
        """Eager-load aircraft, member, instructor for list/detail responses"""
        return (
            selectinload(Reservation.aircraft),
            selectinload(Reservation.member),
            selectinload(Reservation.instructor),
        )

    async def get_all_for_club(
        self, club_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Reservation], int]:
        """Get all reservations for a club (admin view) with pagination"""
        async with self.db_svc.get_sessionmaker()() as session:
            count_stmt = (
                select(func.count())  # pylint: disable=not-callable
                .select_from(Reservation)
                .where(Reservation.club_id == club_id)
            )
            total = await session.scalar(count_stmt)

            stmt = (
                select(Reservation)
                .where(Reservation.club_id == club_id)
                .options(*self._with_relations())
                .order_by(Reservation.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all()), total or 0

    async def get_for_member(
        self, member_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Reservation], int]:
        """Get all reservations for a specific member with pagination"""
        async with self.db_svc.get_sessionmaker()() as session:
            count_stmt = (
                select(func.count())  # pylint: disable=not-callable
                .select_from(Reservation)
                .where(Reservation.member_id == member_id)
            )
            total = await session.scalar(count_stmt)

            stmt = (
                select(Reservation)
                .where(Reservation.member_id == member_id)
                .options(*self._with_relations())
                .order_by(Reservation.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all()), total or 0

    async def get_for_instructor(
        self, instructor_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Reservation], int]:
        """Get all reservations where this user is the instructor
        with pagination"""
        async with self.db_svc.get_sessionmaker()() as session:
            count_stmt = (
                select(func.count())  # pylint: disable=not-callable
                .select_from(Reservation)
                .where(Reservation.instructor_id == instructor_id)
            )
            total = await session.scalar(count_stmt)

            stmt = (
                select(Reservation)
                .where(Reservation.instructor_id == instructor_id)
                .options(*self._with_relations())
                .order_by(Reservation.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all()), total or 0

    async def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """Get a reservation by id with relations loaded"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Reservation)
                .where(Reservation.id == reservation_id)
                .options(*self._with_relations())
            )
            return result.scalar_one_or_none()

    async def create(
        self, club_id: int, member_id: int, data: ReservationCreate
    ) -> Reservation:
        """Create a new reservation"""
        async with self.db_svc.get_sessionmaker()() as session:
            reservation = Reservation(
                club_id=club_id,
                member_id=member_id,
                aircraft_id=data.aircraft_id,
                instructor_id=data.instructor_id,
                start_time=data.start_time,
                end_time=data.end_time,
                notes=data.notes,
                status=ReservationStatus.CONFIRMED,
            )
            session.add(reservation)
            await session.commit()
            await session.refresh(reservation)
            logger.info("Reservation created: %s", reservation.id)
            # Reload with relations
            return await self.get_by_id(reservation.id)

    async def update(
        self,
        reservation_id: int,
        data: ReservationUpdate,
    ) -> Optional[Reservation]:
        """Update allowed reservation fields"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Reservation).where(Reservation.id == reservation_id)
            )
            reservation = result.scalar_one_or_none()
            if not reservation:
                return None
            for field, value in data.model_dump(exclude_none=True).items():
                setattr(reservation, field, value)
            await session.commit()
            logger.info("Reservation updated: %s", reservation_id)
        return await self.get_by_id(reservation_id)

    async def cancel(self, reservation_id: int) -> Optional[Reservation]:
        """Set reservation status to cancelled"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Reservation).where(Reservation.id == reservation_id)
            )
            reservation = result.scalar_one_or_none()
            if not reservation:
                return None
            reservation.status = ReservationStatus.CANCELLED
            await session.commit()
            logger.info("Reservation cancelled: %s", reservation_id)
        return await self.get_by_id(reservation_id)

    async def complete(
        self,
        reservation_id: int,
        hobbs_start: float,
        hobbs_end: float,
    ) -> Optional[Reservation]:
        """Complete a reservation: record hobbs hours and update
        aircraft total"""
        async with self.db_svc.get_sessionmaker()() as session:
            result = await session.execute(
                select(Reservation).where(Reservation.id == reservation_id)
            )
            reservation = result.scalar_one_or_none()
            if not reservation:
                return None
            reservation.hobbs_start = hobbs_start
            reservation.hobbs_end = hobbs_end
            reservation.status = ReservationStatus.COMPLETED

            # Update aircraft total hobbs hours
            ac_result = await session.execute(
                select(Aircraft).where(Aircraft.id == reservation.aircraft_id)
            )
            aircraft = ac_result.scalar_one_or_none()
            if aircraft:
                aircraft.total_hobbs_hours += hobbs_end - hobbs_start

            await session.commit()
            logger.info("Reservation completed: %s", reservation_id)
        return await self.get_by_id(reservation_id)

    # ── Conflict helpers ────────────────────────────────────────────────────

    async def member_is_busy(
        self,
        member_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Returns True if member already has a confirmed booking in
        the window"""
        async with self.db_svc.get_sessionmaker()() as session:
            q = select(Reservation).where(
                and_(
                    Reservation.member_id == member_id,
                    Reservation.status == ReservationStatus.CONFIRMED,
                    Reservation.start_time < end,
                    Reservation.end_time > start,
                )
            )
            if exclude_id:
                q = q.where(Reservation.id != exclude_id)
            result = await session.execute(q)
            return result.scalar_one_or_none() is not None

    async def instructor_is_busy(
        self,
        instructor_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Returns True if instructor already has a confirmed booking
        in the window"""
        async with self.db_svc.get_sessionmaker()() as session:
            q = select(Reservation).where(
                and_(
                    Reservation.instructor_id == instructor_id,
                    Reservation.status == ReservationStatus.CONFIRMED,
                    Reservation.start_time < end,
                    Reservation.end_time > start,
                )
            )
            if exclude_id:
                q = q.where(Reservation.id != exclude_id)
            result = await session.execute(q)
            return result.scalar_one_or_none() is not None
