from src.repositories.users import UserRepository
from src.schemas.auth import LoginRequest, TokenResponse
from src.svc.errsvc import AppError, InvalidCredentialsError
from src.svc.secsvc import SecSvc


class SeshSvc:

    def __init__(self):
        self.user_repo = UserRepository()
        self.sec_svc = SecSvc()

    async def login(self, req: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(req.email)

        if not user or not self.sec_svc.verify_password(
            req.password, user.hashed_password
        ):
            raise InvalidCredentialsError()

        token = self.sec_svc.create_access_token(
            user_id=user.id,
            role=user.role,
        )

        return TokenResponse(
            access_token=token,
            expires_in=self.sec_svc.get_appenv().access_token_expire_seconds,
        )
