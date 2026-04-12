"""User Pydantic schemas"""

from typing import Optional

from pydantic import BaseModel, EmailStr

from src.entities.user import CertificateType, UserRole
from src.schemas.meta import Pagination


class UserCreate(BaseModel):
    """Schema for creating a new user"""

    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    certificate: Optional[CertificateType] = None
    ratings: Optional[str] = None


class UserCreateRequest(BaseModel):
    """User creation request wrapper"""
    user: UserCreate


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


class UserResponseWrapper(BaseModel):
    """User response wrapper"""
    user: UserResponse


class UserListResponse(BaseModel):
    """User list response"""
    users: list[UserResponse]
    pagination: Pagination
