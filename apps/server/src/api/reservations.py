"""Reservations API router"""

from fastapi import APIRouter, Query, Request

from src.core.reservationsvc import ReservationSvc
from src.core.usrsvc import UsrSvc
from src.decorators.auth import protected
from src.schemas.reservation import (FlightCompleteRequestWrapper,
                                     ReservationCreateRequest,
                                     ReservationListResponse,
                                     ReservationResponse,
                                     ReservationResponseWrapper,
                                     ReservationUpdateRequest)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

res_svc = ReservationSvc()
usr_svc = UsrSvc()


@router.get("/", response_model=ReservationListResponse)
@protected()
async def list_reservations(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ReservationListResponse:
    """
    Admin → all reservations in the club.
    Member/Instructor → their own reservations.
    """
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    user = await usr_svc.get_me(user_id)

    reservations, total = await res_svc.list_reservations(
        user_id, role, user.club_id, page, limit
    )

    return {
        "reservations": [
            ReservationResponse.model_validate(r) for r in reservations
        ],
        "pagination": {"page": page, "limit": limit, "total": total},
    }


@router.get("/{reservation_id}", response_model=ReservationResponseWrapper)
@protected()
async def get_reservation(
    reservation_id: int, request: Request
) -> ReservationResponseWrapper:
    """Get a single reservation. Members can only see their own."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    reservation = await res_svc.get_reservation(reservation_id, user_id, role)

    return {"reservation": ReservationResponse.model_validate(reservation)}


@router.post("/", response_model=ReservationResponseWrapper, status_code=201)
@protected()
async def create_reservation(
    req: ReservationCreateRequest, request: Request
) -> ReservationResponseWrapper:
    """Create a reservation. Enforces all double-booking rules."""
    user_id = int(request.state.user["sub"])
    data = req.reservation

    user = await usr_svc.get_me(user_id)

    reservation = await res_svc.create_reservation(user_id, user.club_id, data)
    return {"reservation": ReservationResponse.model_validate(reservation)}


@router.patch("/{reservation_id}", response_model=ReservationResponseWrapper)
@protected()
async def update_reservation(
    reservation_id: int, req: ReservationUpdateRequest, request: Request
) -> ReservationResponseWrapper:
    """Edit time window or instructor. Members can only edit their own
    confirmed reservations."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]
    data = req.reservation

    updated = await res_svc.update_reservation(
        reservation_id, user_id, role, data
    )
    return {"reservation": ReservationResponse.model_validate(updated)}


@router.delete("/{reservation_id}", response_model=ReservationResponseWrapper)
@protected()
async def cancel_reservation(
    reservation_id: int, request: Request
) -> ReservationResponseWrapper:
    """Cancel a reservation."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]

    cancelled = await res_svc.cancel_reservation(reservation_id, user_id, role)
    return {"reservation": ReservationResponse.model_validate(cancelled)}


@router.post(
    "/{reservation_id}/complete", response_model=ReservationResponseWrapper
)
@protected()
async def complete_reservation(
    reservation_id: int, req: FlightCompleteRequestWrapper, request: Request
) -> ReservationResponseWrapper:
    """Log flight completion with hobbs hours."""
    user_id = int(request.state.user["sub"])
    role = request.state.user["role"]
    data = req.flight_data

    completed = await res_svc.complete_reservation(
        reservation_id, user_id, role, data
    )
    return {"reservation": ReservationResponse.model_validate(completed)}
