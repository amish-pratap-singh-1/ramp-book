"""Reservations API router"""

from fastapi import APIRouter, Query, Request

from src.decorators.auth import protected
from src.entities.reservation import ReservationStatus
from src.entities.user import UserRole
from src.repositories.aircraft import AircraftRepository
from src.repositories.reservations import ReservationRepository
from src.repositories.users import UserRepository
from src.schemas.reservation import (
    FlightCompleteRequestWrapper,
    ReservationCreateRequest,
    ReservationListResponse,
    ReservationResponse,
    ReservationResponseWrapper,
    ReservationUpdateRequest,
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


@router.get("/", response_model=ReservationListResponse)
@protected()
async def list_reservations(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> ReservationListResponse:
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
        reservations, total = await res_repo.get_all_for_club(user.club_id, page, limit)
    elif role == UserRole.INSTRUCTOR:
        reservations, total = await res_repo.get_for_instructor(user_id, page, limit)
    else:
        reservations, total = await res_repo.get_for_member(user_id, page, limit)

    return {
        "reservations": [ReservationResponse.model_validate(r) for r in reservations],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }


@router.get("/{reservation_id}", response_model=ReservationResponseWrapper)
@protected()
async def get_reservation(
    reservation_id: int, request: Request
) -> ReservationResponseWrapper:
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

    return {"reservation": ReservationResponse.model_validate(reservation)}


@router.post("/", response_model=ReservationResponseWrapper, status_code=201)
@protected()
async def create_reservation(
    req: ReservationCreateRequest, request: Request
) -> ReservationResponseWrapper:
    """Create a reservation. Enforces all double-booking rules."""
    user_id = int(request.state.user["sub"])
    data = req.reservation

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
    return {"reservation": ReservationResponse.model_validate(reservation)}


@router.patch("/{reservation_id}", response_model=ReservationResponseWrapper)
@protected()
async def update_reservation(
    reservation_id: int, req: ReservationUpdateRequest, request: Request
) -> ReservationResponseWrapper:
    """Edit time window or instructor. Members can only edit their own confirmed reservations."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]
    data = req.reservation

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
    return {"reservation": ReservationResponse.model_validate(updated)}


@router.delete("/{reservation_id}", response_model=ReservationResponseWrapper)
@protected()
async def cancel_reservation(
    reservation_id: int, request: Request
) -> ReservationResponseWrapper:
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
    return {"reservation": ReservationResponse.model_validate(cancelled)}


@router.post("/{reservation_id}/complete", response_model=ReservationResponseWrapper)
@protected()
async def complete_reservation(
    reservation_id: int, req: FlightCompleteRequestWrapper, request: Request
) -> ReservationResponseWrapper:
    """Log flight completion with hobbs hours."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]
    data = req.flight_data

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
    return {"reservation": ReservationResponse.model_validate(completed)}
