"""Users API router"""

from fastapi import APIRouter, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.repositories.users import UserRepository
from src.schemas.user import UserResponse
from src.svc.errsvc import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])

user_repo = UserRepository()


@router.get("/me", response_model=UserResponse)
@protected()
async def me(request: Request) -> UserResponse:
    """Get current authenticated user info"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    return UserResponse.model_validate(user)


@router.get("/instructors", response_model=list[UserResponse])
@protected()
async def list_instructors(request: Request) -> list[UserResponse]:
    """List all active instructors in the club"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    instructors = await user_repo.get_instructors(user.club_id)
    return [UserResponse.model_validate(i) for i in instructors]
