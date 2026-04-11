"""Reservations API router"""

from fastapi import APIRouter, Request

from src.decorators.auth import protected
from src.entities.reservation import ReservationStatus
from src.entities.user import UserRole
from src.repositories.aircraft import AircraftRepository
from src.repositories.reservations import ReservationRepository
from src.repositories.users import UserRepository
from src.schemas.reservation import (
    FlightCompleteRequest,
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
)
from src.svc.errsvc import (
    ConflictError,
    ForbiddenError,
    ResourceNotFoundError,
    UserNotFoundError,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

res_repo = ReservationRepository()
aircraft_repo = AircraftRepository()
user_repo = UserRepository()


@router.get("/", response_model=list[ReservationResponse])
@protected()
async def list_reservations(request: Request) -> list[ReservationResponse]:
    """
    Admin → all reservations in the club.
    Member/Instructor → their own reservations.
    """
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()

    if role == UserRole.ADMIN:
        reservations = await res_repo.get_all_for_club(user.club_id)
    elif role == UserRole.INSTRUCTOR:
        reservations = await res_repo.get_for_instructor(user_id)
    else:
        reservations = await res_repo.get_for_member(user_id)

    return [ReservationResponse.model_validate(r) for r in reservations]


@router.get("/{reservation_id}", response_model=ReservationResponse)
@protected()
async def get_reservation(
    reservation_id: int, request: Request
) -> ReservationResponse:
    """Get a single reservation. Members can only see their own."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    reservation = await res_repo.get_by_id(reservation_id)
    if not reservation:
        raise ResourceNotFoundError("Reservation not found")

    # Non-admins may only view their own
    if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
        if str(reservation.member_id) != str(user_id) and str(
            reservation.instructor_id
        ) != str(user_id):
            raise ForbiddenError()

    return ReservationResponse.model_validate(reservation)


@router.post("/", response_model=ReservationResponse, status_code=201)
@protected()
async def create_reservation(
    data: ReservationCreate, request: Request
) -> ReservationResponse:
    """Create a reservation. Enforces all double-booking rules."""
    user_id = int(request.state.user["sub"])

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()

    # 1. Aircraft availability (also checks maintenance windows)
    aircraft_ok = await aircraft_repo.is_available(
        data.aircraft_id, data.start_time, data.end_time
    )
    if not aircraft_ok:
        raise ConflictError(
            "Aircraft is already booked or under maintenance in that window"
        )

    # 2. Member double-booking
    if await res_repo.member_is_busy(user_id, data.start_time, data.end_time):
        raise ConflictError("You already have a reservation in that time window")

    # 3. Instructor double-booking
    if data.instructor_id:
        if await res_repo.instructor_is_busy(
            data.instructor_id, data.start_time, data.end_time
        ):
            raise ConflictError(
                "Selected instructor is already booked in that time window"
            )

    reservation = await res_repo.create(user.club_id, user_id, data)
    return ReservationResponse.model_validate(reservation)


@router.patch("/{reservation_id}", response_model=ReservationResponse)
@protected()
async def update_reservation(
    reservation_id: int, data: ReservationUpdate, request: Request
) -> ReservationResponse:
    """Edit time window or instructor. Members can only edit their own confirmed reservations."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    reservation = await res_repo.get_by_id(reservation_id)
    if not reservation:
        raise ResourceNotFoundError("Reservation not found")

    # Ownership check for non-admins
    if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
        if str(reservation.member_id) != str(user_id):
            raise ForbiddenError()

    if reservation.status != ReservationStatus.CONFIRMED:
        raise ConflictError("Only confirmed reservations can be edited")

    # Re-run availability checks with new times / instructor
    new_start = data.start_time or reservation.start_time
    new_end = data.end_time or reservation.end_time
    new_instr = (
        data.instructor_id
        if data.instructor_id is not None
        else reservation.instructor_id
    )

    if data.start_time or data.end_time:
        aircraft_ok = await aircraft_repo.is_available(
            reservation.aircraft_id,
            new_start,
            new_end,
            exclude_reservation_id=reservation_id,
        )
        if not aircraft_ok:
            raise ConflictError(
                "Aircraft is already booked or under maintenance in that window"
            )

        if await res_repo.member_is_busy(
            user_id, new_start, new_end, exclude_id=reservation_id
        ):
            raise ConflictError("You already have a reservation in that time window")

    if new_instr and new_instr != reservation.instructor_id:
        if await res_repo.instructor_is_busy(
            new_instr, new_start, new_end, exclude_id=reservation_id
        ):
            raise ConflictError(
                "Selected instructor is already booked in that time window"
            )

    updated = await res_repo.update(reservation_id, data)
    return ReservationResponse.model_validate(updated)


@router.delete("/{reservation_id}", response_model=ReservationResponse)
@protected()
async def cancel_reservation(
    reservation_id: int, request: Request
) -> ReservationResponse:
    """Cancel a reservation."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    reservation = await res_repo.get_by_id(reservation_id)
    if not reservation:
        raise ResourceNotFoundError("Reservation not found")

    if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
        if str(reservation.member_id) != str(user_id):
            raise ForbiddenError()

    if reservation.status != ReservationStatus.CONFIRMED:
        raise ConflictError("Only confirmed reservations can be cancelled")

    cancelled = await res_repo.cancel(reservation_id)
    return ReservationResponse.model_validate(cancelled)


@router.post("/{reservation_id}/complete", response_model=ReservationResponse)
@protected()
async def complete_reservation(
    reservation_id: int, data: FlightCompleteRequest, request: Request
) -> ReservationResponse:
    """Log flight completion with hobbs hours."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    reservation = await res_repo.get_by_id(reservation_id)
    if not reservation:
        raise ResourceNotFoundError("Reservation not found")

    if role not in (UserRole.ADMIN, UserRole.ADMIN.value):
        if str(reservation.member_id) != str(user_id):
            raise ForbiddenError()

    if reservation.status == ReservationStatus.COMPLETED:
        raise ConflictError("Flight has already been logged")
    if reservation.status == ReservationStatus.CANCELLED:
        raise ConflictError("Cannot complete a cancelled reservation")

    completed = await res_repo.complete(reservation_id, data.hobbs_start, data.hobbs_end)
    return ReservationResponse.model_validate(completed)
