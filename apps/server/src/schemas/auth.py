"""Authentication related object definition"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request body"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Login response body"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
