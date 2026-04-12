"""Reservation Pydantic schemas"""

import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from src.entities.reservation import ReservationStatus
from src.schemas.meta import Pagination


class ReservationCreate(BaseModel):
    """Schema for creating a reservation"""

    aircraft_id: int
    instructor_id: Optional[int] = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    notes: Optional[str] = None

    @model_validator(mode="after")
    def end_after_start(self) -> "ReservationCreate":
        """Ensure end_time is after start_time"""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ReservationCreateRequest(BaseModel):
    """Reservation creation request wrapper"""

    reservation: ReservationCreate


class ReservationUpdate(BaseModel):
    """Schema for updating a reservation (time window / instructor only)"""

    instructor_id: Optional[int] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def end_after_start(self) -> "ReservationUpdate":
        """Time constraint check"""
        if (
            self.start_time
            and self.end_time
            and self.end_time <= self.start_time
        ):
            raise ValueError("end_time must be after start_time")
        return self


class ReservationUpdateRequest(BaseModel):
    """Reservation update request wrapper"""

    reservation: ReservationUpdate


class FlightCompleteRequest(BaseModel):
    """Schema for completing a flight (entering hobbs hours)"""

    hobbs_start: float
    hobbs_end: float

    @model_validator(mode="after")
    def round_hours(self) -> "FlightCompleteRequest":
        """Round to 2 decimals"""
        self.hobbs_start = round(self.hobbs_start, 2)
        self.hobbs_end = round(self.hobbs_end, 2)
        return self

    @model_validator(mode="after")
    def end_after_start(self) -> "FlightCompleteRequest":
        """Time constraint check"""
        if self.hobbs_end <= self.hobbs_start:
            raise ValueError("hobbs_end must be greater than hobbs_start")
        return self


class FlightCompleteRequestWrapper(BaseModel):
    """Flight complete request wrapper"""

    flight_data: FlightCompleteRequest


class ReservationMemberInfo(BaseModel):
    """Nested member info"""

    id: int
    full_name: str
    email: str

    model_config = {"from_attributes": True}


class ReservationAircraftInfo(BaseModel):
    """Nested aircraft info"""

    id: int
    tail_number: str
    model: str
    hourly_rate_usd: float

    model_config = {"from_attributes": True}


class ReservationResponse(BaseModel):
    """Schema for reservation response"""

    id: int
    club_id: int
    aircraft_id: int
    member_id: int
    instructor_id: Optional[int] = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: ReservationStatus
    hobbs_start: Optional[float] = None
    hobbs_end: Optional[float] = None
    notes: Optional[str] = None
    aircraft: Optional[ReservationAircraftInfo] = None
    member: Optional[ReservationMemberInfo] = None
    instructor: Optional[ReservationMemberInfo] = None

    model_config = {"from_attributes": True}


class ReservationResponseWrapper(BaseModel):
    """Reservation response wrapper"""

    reservation: ReservationResponse


class ReservationListResponse(BaseModel):
    """Reservation list response"""

    reservations: list[ReservationResponse]
    pagination: Pagination
