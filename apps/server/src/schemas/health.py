"""Application health related object definition"""

from pydantic import BaseModel

class HealthResponse(BaseModel):
    """Application health response"""
    status: str
    message: str