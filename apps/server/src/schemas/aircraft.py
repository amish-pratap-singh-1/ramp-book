"""Aircraft Pydantic schemas"""

from typing import Optional

from pydantic import BaseModel

from src.entities.aircraft import AircraftStatus


class AircraftCreate(BaseModel):
    """Schema for creating an aircraft"""

    tail_number: str
    model: str
    year: int
    hourly_rate_usd: float
    total_hobbs_hours: float = 0.0
    notes: Optional[str] = None


class AircraftUpdate(BaseModel):
    """Schema for updating an aircraft"""

    model: Optional[str] = None
    year: Optional[int] = None
    hourly_rate_usd: Optional[float] = None
    total_hobbs_hours: Optional[float] = None
    status: Optional[AircraftStatus] = None
    notes: Optional[str] = None


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
