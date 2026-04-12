"""Admin API router"""

from fastapi import APIRouter, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.repositories.maintenance import MaintenanceRepository
from src.repositories.reservations import ReservationRepository
from src.repositories.users import UserRepository
from src.schemas.maintenance import (
    MaintenanceWindowCreate,
    MaintenanceWindowResponse,
)
from src.schemas.reservation import ReservationResponse
from src.schemas.user import UserCreate, UserResponse
from src.svc.errsvc import ResourceNotFoundError, UserNotFoundError

router = APIRouter(prefix="/admin", tags=["Admin"])

res_repo = ReservationRepository()
maint_repo = MaintenanceRepository()
user_repo = UserRepository()


@router.get("/reservations", response_model=list[ReservationResponse])
@protected(UserRole.ADMIN)
async def all_reservations(request: Request) -> list[ReservationResponse]:
    """Get all reservations across the club (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    reservations = await res_repo.get_all_for_club(user.club_id)
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.get("/maintenance", response_model=list[MaintenanceWindowResponse])
@protected(UserRole.ADMIN)
async def list_maintenance(request: Request) -> list[MaintenanceWindowResponse]:
    """List all maintenance windows (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    windows = await maint_repo.get_all(user.club_id)
    return [MaintenanceWindowResponse.model_validate(w) for w in windows]


@router.post("/maintenance", response_model=MaintenanceWindowResponse, status_code=201)
@protected(UserRole.ADMIN)
async def create_maintenance(
    data: MaintenanceWindowCreate, request: Request
) -> MaintenanceWindowResponse:
    """Create a maintenance window (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    window = await maint_repo.create(user.club_id, data)
    return MaintenanceWindowResponse.model_validate(window)


@router.delete("/maintenance/{window_id}", status_code=204)
@protected(UserRole.ADMIN)
async def delete_maintenance(window_id: int, request: Request) -> None:
    """Delete a maintenance window (admin only)"""
    deleted = await maint_repo.delete(window_id)
    if not deleted:
        raise ResourceNotFoundError("Maintenance window not found")

@router.get("/users", response_model=list[UserResponse])
@protected(UserRole.ADMIN)
async def list_users(request: Request) -> list[UserResponse]:
    """List all users (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    users = await user_repo.get_all(user.club_id)
    return [UserResponse.model_validate(u) for u in users]

@router.post("/users", response_model=UserResponse, status_code=201)
@protected(UserRole.ADMIN)
async def create_user(data: UserCreate, request: Request) -> UserResponse:
    """Create a new user (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    # Check if email is taken
    existing = await user_repo.get_by_email(data.email)
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = await user_repo.create(user.club_id, data)
    return UserResponse.model_validate(new_user)
