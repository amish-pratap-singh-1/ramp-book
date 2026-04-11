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


@router.get("/admin/dashboard")
@protected(UserRole.ADMIN)
async def admin_dashboard(request: Request):
    user_id = int(request.state.user["sub"])
    return {"user_id": user_id}


@router.get("/instructor/courses")
@protected(UserRole.INSTRUCTOR, UserRole.ADMIN)
async def list_courses(request: Request):
    return {"courses": []}


@router.get("/me")
@protected()
async def me(request: Request):
    return request.state.user
