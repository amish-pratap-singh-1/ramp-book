"""Authentication related object definition"""

from pydantic import BaseModel, EmailStr


class UserLoginData(BaseModel):
    """User login data"""

    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Login request body"""

    user: UserLoginData


class UserTokenData(BaseModel):
    """User token data"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenResponse(BaseModel):
    """Login response body"""

    user: UserTokenData
