"""Maintenance window Pydantic schemas"""

import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from src.schemas.meta import Pagination


class MaintenanceWindowCreate(BaseModel):
    """Schema for creating a maintenance window"""

    aircraft_id: int
    start_time: datetime.datetime
    end_time: datetime.datetime
    reason: Optional[str] = None

    @model_validator(mode="after")
    def end_after_start(self) -> "MaintenanceWindowCreate":
        """Time constraint check"""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class MaintenanceWindowCreateRequest(BaseModel):
    """Maintenance window creation request wrapper"""

    maintenance_window: MaintenanceWindowCreate


class MaintenanceWindowResponse(BaseModel):
    """Schema for maintenance window response"""

    id: int
    club_id: int
    aircraft_id: int
    start_time: datetime.datetime
    end_time: datetime.datetime
    reason: Optional[str] = None

    model_config = {"from_attributes": True}


class MaintenanceWindowResponseWrapper(BaseModel):
    """Maintenance window response wrapper"""

    maintenance_window: MaintenanceWindowResponse


class MaintenanceWindowListResponse(BaseModel):
    """Maintenance window list response"""

    maintenance_windows: list[MaintenanceWindowResponse]
    pagination: Pagination
