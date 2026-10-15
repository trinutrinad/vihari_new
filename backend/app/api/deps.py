"""FastAPI dependencies for auth and RBAC."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.models import User
from app.services.auth import AuthService, parse_bearer_user_id

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(db)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Not authenticated")
    user_id = parse_bearer_user_id(credentials.credentials)
    user = AuthService(db).get_user(user_id)
    if not user.is_active:
        raise ForbiddenError("Account is deactivated")
    return user


def get_current_user_optional(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User | None:
    if credentials is None:
        return None
    try:
        return get_current_user(db=db, credentials=credentials)
    except (UnauthorizedError, ForbiddenError):
        return None


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = set(roles)

    def _dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        role_names = {role.name for role in user.roles} | {user.primary_role}
        if user.primary_role == "SUPER_ADMIN" or "SUPER_ADMIN" in role_names:
            return user
        if role_names.isdisjoint(allowed):
            raise ForbiddenError("Insufficient permissions")
        return user

    return _dependency


def client_meta(
    user_agent: Annotated[str | None, Header(alias="User-Agent")] = None,
    x_forwarded_for: Annotated[str | None, Header(alias="X-Forwarded-For")] = None,
) -> tuple[str | None, str | None]:
    ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else None
    return user_agent, ip


CurrentUser = Annotated[User, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
DbSession = Annotated[Session, Depends(get_db)]
UserId = UUID
