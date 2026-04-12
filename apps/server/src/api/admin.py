"""Admin API router"""

from fastapi import APIRouter, Query, Request

from src.core.aircraftsvc import AircraftSvc
from src.core.reservationsvc import ReservationSvc
from src.core.usrsvc import UsrSvc
from src.decorators.auth import protected
from src.entities.user import UserRole
from src.schemas.maintenance import (MaintenanceWindowCreateRequest,
                                     MaintenanceWindowListResponse,
                                     MaintenanceWindowResponse,
                                     MaintenanceWindowResponseWrapper)
from src.schemas.reservation import (ReservationListResponse,
                                     ReservationResponse)
from src.schemas.user import (UserCreateRequest, UserListResponse,
                              UserResponse, UserResponseWrapper)
from src.svc.errsvc import ErrSvc

router = APIRouter(prefix="/admin", tags=["Admin"])

aircraft_svc = AircraftSvc()
res_svc = ReservationSvc()
usr_svc = UsrSvc()


@router.get("/reservations", response_model=ReservationListResponse)
@protected(UserRole.ADMIN)
async def all_reservations(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ReservationListResponse:
    """Get all reservations across the club (admin only)"""
    try:
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
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.get("/maintenance", response_model=MaintenanceWindowListResponse)
@protected()
async def list_maintenance(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    aircraft_id: int | None = Query(None),
) -> MaintenanceWindowListResponse:
    """List maintenance windows (optionally filtered by aircraft)"""
    try:
        user_id = int(request.state.user["sub"])
        user = await usr_svc.get_me(user_id)

        windows, total = await aircraft_svc.list_maintenance(
            user.club_id, page, limit, aircraft_id
        )

        return {
            "maintenance_windows": [
                MaintenanceWindowResponse.model_validate(w) for w in windows
            ],
            "pagination": {"page": page, "limit": limit, "total": total},
        }
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.post(
    "/maintenance",
    response_model=MaintenanceWindowResponseWrapper,
    status_code=201,
)
@protected(UserRole.ADMIN)
async def create_maintenance(
    req: MaintenanceWindowCreateRequest, request: Request
) -> MaintenanceWindowResponseWrapper:
    """Create a maintenance window (admin only)"""
    try:
        user_id = int(request.state.user["sub"])
        user = await usr_svc.get_me(user_id)

        window = await aircraft_svc.create_maintenance(
            user.club_id, req.maintenance_window
        )
        return {
            "maintenance_window": MaintenanceWindowResponse.model_validate(
                window
            )
        }
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.delete("/maintenance/{window_id}", status_code=204)
@protected(UserRole.ADMIN)
async def delete_maintenance(window_id: int) -> None:
    """Delete a maintenance window (admin only)"""
    try:
        await aircraft_svc.delete_maintenance(window_id)
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.get("/users", response_model=UserListResponse)
@protected(UserRole.ADMIN)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    """List all users (admin only)"""
    try:
        user_id = int(request.state.user["sub"])

        users, total = await usr_svc.list_users(user_id, page, limit)

        return {
            "users": [UserResponse.model_validate(u) for u in users],
            "pagination": {"page": page, "limit": limit, "total": total},
        }
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.post("/users", response_model=UserResponseWrapper, status_code=201)
@protected(UserRole.ADMIN)
async def create_user(
    req: UserCreateRequest, request: Request
) -> UserResponseWrapper:
    """Create a new user (admin only)"""
    try:
        user_id = int(request.state.user["sub"])

        new_user = await usr_svc.create_user(user_id, req.user)
        return {"user": UserResponse.model_validate(new_user)}
    except Exception as e:
        raise ErrSvc.handle_api_error(e)
