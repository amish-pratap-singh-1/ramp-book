"""Reservation service module"""

import logging
from typing import Optional

from src.entities.reservation import Reservation, ReservationStatus
from src.entities.user import UserRole
from src.repositories.aircraft import AircraftRepository
from src.repositories.reservations import ReservationRepository
from src.repositories.users import UserRepository
from src.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    FlightCompleteRequest,
)
from src.svc.errsvc import (
    ConflictError,
    ForbiddenError,
    ResourceNotFoundError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class ReservationSvc:
    """Class for managing reservation lifecycle and business rules"""

    def __init__(self):
        self.res_repo = ReservationRepository()
        self.aircraft_repo = AircraftRepository()
        self.user_repo = UserRepository()

    async def list_reservations(
        self, user_id: int, role: str, club_id: int, page: int, limit: int
    ) -> tuple[list[Reservation], int]:
        """Context-aware reservation listing"""
        if role == UserRole.ADMIN or role == UserRole.ADMIN.value:
            return await self.res_repo.get_all_for_club(club_id, page, limit)
        elif role == UserRole.INSTRUCTOR or role == UserRole.INSTRUCTOR.value:
            return await self.res_repo.get_for_instructor(user_id, page, limit)
        else:
            return await self.res_repo.get_for_member(user_id, page, limit)

    async def get_reservation(
        self, reservation_id: int, user_id: int, role: str
    ) -> Reservation:
        """Get reservation with ownership/permission check"""
        reservation = await self.res_repo.get_by_id(reservation_id)
        if not reservation:
            raise ResourceNotFoundError("Reservation not found")

        # Non-admins may only view their own
        if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
            if reservation.member_id != user_id and reservation.instructor_id != user_id:
                raise ForbiddenError()

        return reservation

    async def create_reservation(
        self, user_id: int, club_id: int, data: ReservationCreate
    ) -> Reservation:
        """Create a reservation enforcing double-booking rules"""
        # 1. Aircraft availability (also checks maintenance windows)
        aircraft_ok = await self.aircraft_repo.is_available(
            data.aircraft_id, data.start_time, data.end_time
        )
        if not aircraft_ok:
            raise ConflictError(
                "Aircraft is already booked or under maintenance in that window"
            )

        # 2. Member double-booking
        if await self.res_repo.member_is_busy(user_id, data.start_time, data.end_time):
            raise ConflictError("You already have a reservation in that time window")

        # 3. Instructor double-booking
        if data.instructor_id:
            if await self.res_repo.instructor_is_busy(
                data.instructor_id, data.start_time, data.end_time
            ):
                raise ConflictError(
                    "Selected instructor is already booked in that time window"
                )

        return await self.res_repo.create(club_id, user_id, data)

    async def update_reservation(
        self, reservation_id: int, user_id: int, role: str, data: ReservationUpdate
    ) -> Reservation:
        """Edit reservation with re-validation of rules"""
        reservation = await self.res_repo.get_by_id(reservation_id)
        if not reservation:
            raise ResourceNotFoundError("Reservation not found")

        # Ownership check for non-admins
        if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
            if reservation.member_id != user_id:
                raise ForbiddenError()

        if reservation.status != ReservationStatus.CONFIRMED:
            raise ConflictError("Only confirmed reservations can be edited")

        # Re-run availability checks if times or instructor changed
        new_start = data.start_time or reservation.start_time
        new_end = data.end_time or reservation.end_time
        new_instr = (
            data.instructor_id
            if data.instructor_id is not None
            else reservation.instructor_id
        )

        if data.start_time or data.end_time:
            aircraft_ok = await self.aircraft_repo.is_available(
                reservation.aircraft_id,
                new_start,
                new_end,
                exclude_reservation_id=reservation_id,
            )
            if not aircraft_ok:
                raise ConflictError(
                    "Aircraft is already booked or under maintenance in that window"
                )

            if await self.res_repo.member_is_busy(
                user_id, new_start, new_end, exclude_id=reservation_id
            ):
                raise ConflictError("You already have a reservation in that time window")

        if new_instr and new_instr != reservation.instructor_id:
            if await self.res_repo.instructor_is_busy(
                new_instr, new_start, new_end, exclude_id=reservation_id
            ):
                raise ConflictError(
                    "Selected instructor is already booked in that time window"
                )

        return await self.res_repo.update(reservation_id, data)

    async def cancel_reservation(
        self, reservation_id: int, user_id: int, role: str
    ) -> Reservation:
        """Cancel a reservation"""
        reservation = await self.res_repo.get_by_id(reservation_id)
        if not reservation:
            raise ResourceNotFoundError("Reservation not found")

        if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
            if reservation.member_id != user_id:
                raise ForbiddenError()

        if reservation.status != ReservationStatus.CONFIRMED:
            raise ConflictError("Only confirmed reservations can be cancelled")

        return await self.res_repo.cancel(reservation_id)

    async def complete_reservation(
        self, reservation_id: int, user_id: int, role: str, data: FlightCompleteRequest
    ) -> Reservation:
        """Log flight completion with hobbs hours"""
        reservation = await self.res_repo.get_by_id(reservation_id)
        if not reservation:
            raise ResourceNotFoundError("Reservation not found")

        if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
            if reservation.member_id != user_id:
                raise ForbiddenError()

        if reservation.status == ReservationStatus.COMPLETED:
            raise ConflictError("Flight has already been logged")
        if reservation.status == ReservationStatus.CANCELLED:
            raise ConflictError("Cannot complete a cancelled reservation")

        return await self.res_repo.complete(reservation_id, data.hobbs_start, data.hobbs_end)
