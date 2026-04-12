"""Aircraft API router"""

from fastapi import APIRouter, Query, Request

from src.core.aircraftsvc import AircraftSvc
from src.core.usrsvc import UsrSvc
from src.decorators.auth import protected
from src.svc.errsvc import ErrSvc
from src.entities.user import UserRole
from src.schemas.aircraft import (AircraftCreateRequest, AircraftListResponse,
                                  AircraftResponse, AircraftResponseWrapper,
                                  AircraftScheduleListResponse,
                                  AircraftUpdateRequest)

router = APIRouter(prefix="/aircraft", tags=["Aircraft"])

aircraft_svc = AircraftSvc()
usr_svc = UsrSvc()


@router.get("/", response_model=AircraftListResponse)
@protected()
async def list_aircraft(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> AircraftListResponse:
    try:
        """List all aircraft in the club fleet"""
        user_id = int(request.state.user["sub"])
        user = await usr_svc.get_me(user_id)

        aircraft, total = await aircraft_svc.list_aircraft(
            user.club_id, page, limit
        )

        return {
            "aircrafts": [AircraftResponse.model_validate(a) for a in aircraft],
            "pagination": {"page": page, "limit": limit, "total": total},
        }
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.get("/{aircraft_id}", response_model=AircraftResponseWrapper)
@protected()
async def get_aircraft(aircraft_id: int) -> AircraftResponseWrapper:
    try:
        """Get a single aircraft by ID"""
        aircraft = await aircraft_svc.get_aircraft(aircraft_id)
        return {"aircraft": AircraftResponse.model_validate(aircraft)}
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.get(
    "/{aircraft_id}/schedule", response_model=AircraftScheduleListResponse
)
@protected()
async def get_aircraft_schedule(
    aircraft_id: int,
) -> AircraftScheduleListResponse:
    try:
        """Get non-identifying overlap schedule for an aircraft to
        power UI blocking"""
        schedules = await aircraft_svc.get_schedule(aircraft_id)

        # Simple pagination for schedule (all items for now but wrapped)
        return {
            "schedules": schedules,
            "pagination": {
                "page": 1,
                "limit": len(schedules),
                "total": len(schedules),
            },
        }
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.post("/", response_model=AircraftResponseWrapper, status_code=201)
@protected(UserRole.ADMIN)
async def create_aircraft(
    req: AircraftCreateRequest, request: Request
) -> AircraftResponseWrapper:
    try:
        """Create a new aircraft (admin only)"""
        user_id = int(request.state.user["sub"])
        user = await usr_svc.get_me(user_id)

        aircraft = await aircraft_svc.create_aircraft(user.club_id, req.aircraft)
        return {"aircraft": AircraftResponse.model_validate(aircraft)}
    except Exception as e:
        raise ErrSvc.handle_api_error(e)


@router.patch("/{aircraft_id}", response_model=AircraftResponseWrapper)
@protected(UserRole.ADMIN)
async def update_aircraft(
    aircraft_id: int, req: AircraftUpdateRequest
) -> AircraftResponseWrapper:
    try:
        """Update aircraft details (admin only)"""
        aircraft = await aircraft_svc.update_aircraft(aircraft_id, req.aircraft)
        return {"aircraft": AircraftResponse.model_validate(aircraft)}
    except Exception as e:
        raise ErrSvc.handle_api_error(e)
