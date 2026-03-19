from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return decode_token(token)
    except ValueError:
        raise UnauthorizedError()


async def get_current_user_id(payload: dict = Depends(get_current_user_payload)) -> int:
    uid = payload.get("sub")
    if not uid:
        raise UnauthorizedError()
    return int(uid)


def require_roles(*roles: UserRole):
    async def checker(payload: dict = Depends(get_current_user_payload)) -> dict:
        role = payload.get("role")
        if role not in [r.value for r in roles]:
            raise ForbiddenError()
        return payload
    return checker


# Convenience
require_admin = require_roles(UserRole.admin)
require_agent_or_admin = require_roles(UserRole.admin, UserRole.agent)
