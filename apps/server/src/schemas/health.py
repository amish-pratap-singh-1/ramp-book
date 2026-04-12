"""Application health related object definition"""

from pydantic import BaseModel


class HealthData(BaseModel):
    """Application health data"""

    status: str
    message: str


class HealthResponse(BaseModel):
    """Application health response wrapper"""

    health: HealthData
