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
