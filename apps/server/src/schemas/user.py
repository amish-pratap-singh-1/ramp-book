"""User Pydantic schemas"""

from typing import Optional

from pydantic import BaseModel, EmailStr

from src.entities.user import CertificateType, UserRole


class UserResponse(BaseModel):
    """Schema for user response"""

    id: int
    club_id: int
    email: EmailStr
    full_name: str
    role: UserRole
    certificate: Optional[CertificateType] = None
    ratings: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}
