"""Authentication api"""

from fastapi import APIRouter, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.schemas.auth import LoginRequest, TokenResponse
from src.svc.seshsvc import SeshSvc

router = APIRouter(tags=["Auth"])

sesh_svc = SeshSvc()


@router.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest) -> TokenResponse:
    """Login api"""
    return await sesh_svc.login(req)
