"""Aircraft API router"""

from fastapi import APIRouter, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.repositories.aircraft import AircraftRepository
from src.repositories.users import UserRepository
from src.schemas.aircraft import AircraftCreate, AircraftResponse, AircraftScheduleItem, AircraftUpdate
from src.svc.errsvc import ResourceNotFoundError, UserNotFoundError

router = APIRouter(prefix="/aircraft", tags=["Aircraft"])

aircraft_repo = AircraftRepository()
user_repo = UserRepository()


@router.get("/", response_model=list[AircraftResponse])
@protected()
async def list_aircraft(request: Request) -> list[AircraftResponse]:
    """List all aircraft in the club fleet"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    aircraft = await aircraft_repo.get_all(user.club_id)
    return [AircraftResponse.model_validate(a) for a in aircraft]


@router.get("/{aircraft_id}", response_model=AircraftResponse)
@protected()
async def get_aircraft(aircraft_id: int, request: Request) -> AircraftResponse:
    """Get a single aircraft by ID"""
    aircraft = await aircraft_repo.get_by_id(aircraft_id)
    if not aircraft:
        raise ResourceNotFoundError("Aircraft not found")
    return AircraftResponse.model_validate(aircraft)


@router.get("/{aircraft_id}/schedule", response_model=list[AircraftScheduleItem])
@protected()
async def get_aircraft_schedule(aircraft_id: int, request: Request) -> list[AircraftScheduleItem]:
    """Get non-identifying overlap schedule for an aircraft to power UI blocking"""
    aircraft = await aircraft_repo.get_by_id(aircraft_id)
    if not aircraft:
        raise ResourceNotFoundError("Aircraft not found")
    # All authenticated users can view an aircraft schedule structure (times)
    return await aircraft_repo.get_schedule(aircraft_id)


@router.post("/", response_model=AircraftResponse, status_code=201)
@protected(UserRole.ADMIN)
async def create_aircraft(
    data: AircraftCreate, request: Request
) -> AircraftResponse:
    """Create a new aircraft (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    aircraft = await aircraft_repo.create(user.club_id, data)
    return AircraftResponse.model_validate(aircraft)


@router.patch("/{aircraft_id}", response_model=AircraftResponse)
@protected(UserRole.ADMIN)
async def update_aircraft(
    aircraft_id: int, data: AircraftUpdate, request: Request
) -> AircraftResponse:
    """Update aircraft details (admin only)"""
    aircraft = await aircraft_repo.update(aircraft_id, data)
    if not aircraft:
        raise ResourceNotFoundError("Aircraft not found")
    return AircraftResponse.model_validate(aircraft)

