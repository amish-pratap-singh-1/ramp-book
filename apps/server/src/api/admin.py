"""Admin API router"""

from fastapi import APIRouter, Query, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.repositories.maintenance import MaintenanceRepository
from src.repositories.reservations import ReservationRepository
from src.repositories.users import UserRepository
from src.schemas.maintenance import (
    MaintenanceWindowCreateRequest,
    MaintenanceWindowListResponse,
    MaintenanceWindowResponse,
    MaintenanceWindowResponseWrapper,
)
from src.schemas.reservation import ReservationListResponse, ReservationResponse
from src.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserResponseWrapper,
)
from src.svc.errsvc import ResourceNotFoundError, UserNotFoundError

router = APIRouter(prefix="/admin", tags=["Admin"])

res_repo = ReservationRepository()
maint_repo = MaintenanceRepository()
user_repo = UserRepository()


@router.get("/reservations", response_model=ReservationListResponse)
@protected(UserRole.ADMIN)
async def all_reservations(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> ReservationListResponse:
    """Get all reservations across the club (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    reservations, total = await res_repo.get_all_for_club(user.club_id, page, limit)
    
    return {
        "reservations": [ReservationResponse.model_validate(r) for r in reservations],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }


@router.get("/maintenance", response_model=MaintenanceWindowListResponse)
@protected(UserRole.ADMIN)
async def list_maintenance(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> MaintenanceWindowListResponse:
    """List all maintenance windows (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    windows, total = await maint_repo.get_all(user.club_id, page, limit)
    
    return {
        "maintenance_windows": [MaintenanceWindowResponse.model_validate(w) for w in windows],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }


@router.post("/maintenance", response_model=MaintenanceWindowResponseWrapper, status_code=201)
@protected(UserRole.ADMIN)
async def create_maintenance(
    req: MaintenanceWindowCreateRequest, request: Request
) -> MaintenanceWindowResponseWrapper:
    """Create a maintenance window (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    window = await maint_repo.create(user.club_id, req.maintenance_window)
    return {"maintenance_window": MaintenanceWindowResponse.model_validate(window)}


@router.delete("/maintenance/{window_id}", status_code=204)
@protected(UserRole.ADMIN)
async def delete_maintenance(window_id: int, request: Request) -> None:
    """Delete a maintenance window (admin only)"""
    deleted = await maint_repo.delete(window_id)
    if not deleted:
        raise ResourceNotFoundError("Maintenance window not found")


@router.get("/users", response_model=UserListResponse)
@protected(UserRole.ADMIN)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> UserListResponse:
    """List all users (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    users, total = await user_repo.get_all(user.club_id, page, limit)
    
    return {
        "users": [UserResponse.model_validate(u) for u in users],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }


@router.post("/users", response_model=UserResponseWrapper, status_code=201)
@protected(UserRole.ADMIN)
async def create_user(req: UserCreateRequest, request: Request) -> UserResponseWrapper:
    """Create a new user (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    data = req.user
    
    # Check if email is taken
    existing = await user_repo.get_by_email(data.email)
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = await user_repo.create(user.club_id, data)
    return {"user": UserResponse.model_validate(new_user)}
