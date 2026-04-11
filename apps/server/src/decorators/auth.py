"""Authentication decorator"""

import functools
import inspect
from typing import Callable

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.entities.user import UserRole
from src.svc.errsvc import InsufficientRoleError, InvalidTokenError
from src.svc.secsvc import AuthSvc

auth_svc = AuthSvc()
_bearer = HTTPBearer()


def protected(*roles: UserRole):
    """Authentication decorator"""
    role_values = {r.value for r in roles}

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        async def wrapper(
            *args,
            credentials: HTTPAuthorizationCredentials = Depends(_bearer),
            **kwargs
        ):
            try:
                token = credentials.credentials
                payload = auth_svc.auth(token, *role_values)

            except InvalidTokenError:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token."},
                )
            except InsufficientRoleError:
                return JSONResponse(
                    status_code=403, content={"detail": "Insufficient role."}
                )

            # Inject into request.state if request is present
            request: Request = kwargs.get("request") or next(
                (a for a in args if isinstance(a, Request)), None
            )
            if request:
                request.state.user = payload

            return await func(*args, **kwargs)

        # Patch the signature so FastAPI picks up the injected `credentials`
        # param
        original_sig = inspect.signature(func)
        credentials_param = inspect.Parameter(
            "credentials",
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=Depends(_bearer),
            annotation=HTTPAuthorizationCredentials,
        )
        new_sig = original_sig.replace(
            parameters=[*original_sig.parameters.values(), credentials_param]
        )
        wrapper.__signature__ = new_sig

        return wrapper

    return decorator
