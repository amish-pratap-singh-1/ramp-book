from fastapi import APIRouter

from src.schemas.auth import LoginRequest, TokenResponse
from src.svc.seshsvc import SeshSvc

router = APIRouter(tags=["Auth"])

sesh_svc = SeshSvc()


@router.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest) -> TokenResponse:
    return await sesh_svc.login(req)
