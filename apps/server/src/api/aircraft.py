"""Aircraft API router"""

from fastapi import APIRouter, Query, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.repositories.aircraft import AircraftRepository
from src.repositories.users import UserRepository
from src.schemas.aircraft import (
    AircraftCreateRequest,
    AircraftListResponse,
    AircraftResponse,
    AircraftResponseWrapper,
    AircraftScheduleListResponse,
    AircraftUpdateRequest,
)
from src.svc.errsvc import ResourceNotFoundError, UserNotFoundError

router = APIRouter(prefix="/aircraft", tags=["Aircraft"])

aircraft_repo = AircraftRepository()
user_repo = UserRepository()


@router.get("/", response_model=AircraftListResponse)
@protected()
async def list_aircraft(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> AircraftListResponse:
    """List all aircraft in the club fleet"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    aircraft, total = await aircraft_repo.get_all(user.club_id, page, limit)
    
    return {
        "aircrafts": [AircraftResponse.model_validate(a) for a in aircraft],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }


@router.get("/{aircraft_id}", response_model=AircraftResponseWrapper)
@protected()
async def get_aircraft(aircraft_id: int, request: Request) -> AircraftResponseWrapper:
    """Get a single aircraft by ID"""
    aircraft = await aircraft_repo.get_by_id(aircraft_id)
    if not aircraft:
        raise ResourceNotFoundError("Aircraft not found")
    return {"aircraft": AircraftResponse.model_validate(aircraft)}


@router.get("/{aircraft_id}/schedule", response_model=AircraftScheduleListResponse)
@protected()
async def get_aircraft_schedule(
    aircraft_id: int, 
    request: Request
) -> AircraftScheduleListResponse:
    """Get non-identifying overlap schedule for an aircraft to power UI blocking"""
    aircraft = await aircraft_repo.get_by_id(aircraft_id)
    if not aircraft:
        raise ResourceNotFoundError("Aircraft not found")
    
    schedules = await aircraft_repo.get_schedule(aircraft_id)
    
    # Simple pagination for schedule (all items for now but wrapped)
    return {
        "schedules": schedules,
        "pagination": {
            "page": 1,
            "limit": len(schedules),
            "total": len(schedules)
        }
    }


@router.post("/", response_model=AircraftResponseWrapper, status_code=201)
@protected(UserRole.ADMIN)
async def create_aircraft(
    req: AircraftCreateRequest, request: Request
) -> AircraftResponseWrapper:
    """Create a new aircraft (admin only)"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    
    aircraft = await aircraft_repo.create(user.club_id, req.aircraft)
    return {"aircraft": AircraftResponse.model_validate(aircraft)}


@router.patch("/{aircraft_id}", response_model=AircraftResponseWrapper)
@protected(UserRole.ADMIN)
async def update_aircraft(
    aircraft_id: int, req: AircraftUpdateRequest, request: Request
) -> AircraftResponseWrapper:
    """Update aircraft details (admin only)"""
    aircraft = await aircraft_repo.update(aircraft_id, req.aircraft)
    if not aircraft:
        raise ResourceNotFoundError("Aircraft not found")
    return {"aircraft": AircraftResponse.model_validate(aircraft)}
