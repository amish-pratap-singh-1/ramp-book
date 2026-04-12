"""Aircraft Pydantic schemas"""

from typing import Optional

from pydantic import BaseModel

from src.entities.aircraft import AircraftStatus
from src.schemas.meta import Pagination


class AircraftCreate(BaseModel):
    """Schema for creating an aircraft"""

    tail_number: str
    model: str
    year: int
    hourly_rate_usd: float
    total_hobbs_hours: float = 0.0
    notes: Optional[str] = None


class AircraftCreateRequest(BaseModel):
    """Aircraft creation request wrapper"""

    aircraft: AircraftCreate


class AircraftUpdate(BaseModel):
    """Schema for updating an aircraft"""

    model: Optional[str] = None
    year: Optional[int] = None
    hourly_rate_usd: Optional[float] = None
    total_hobbs_hours: Optional[float] = None
    status: Optional[AircraftStatus] = None
    notes: Optional[str] = None


class AircraftUpdateRequest(BaseModel):
    """Aircraft update request wrapper"""

    aircraft: AircraftUpdate


class AircraftResponse(BaseModel):
    """Schema for aircraft response"""

    id: int
    club_id: int
    tail_number: str
    model: str
    year: int
    hourly_rate_usd: float
    total_hobbs_hours: float
    status: AircraftStatus
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class AircraftResponseWrapper(BaseModel):
    """Aircraft response wrapper"""

    aircraft: AircraftResponse


class AircraftListResponse(BaseModel):
    """Aircraft list response"""

    aircraft: list[AircraftResponse]
    pagination: Pagination


class AircraftScheduleItem(BaseModel):
    """Schema for a scheduled block (reservation or maintenance)"""

    id: int
    start_time: str
    end_time: str
    type: str  # 'reservation' | 'maintenance'


class AircraftScheduleListResponse(BaseModel):
    """Aircraft schedule list response"""

    schedules: list[AircraftScheduleItem]
    pagination: Pagination
