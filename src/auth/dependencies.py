from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidTokenError, NotAuthenticatedError
from src.auth.models import User
from src.auth.service import AuthService, decode_access_token
from src.core.database import get_db

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if credentials is None:
        raise NotAuthenticatedError()

    user_id = decode_access_token(credentials.credentials)
    user = await AuthService(db).get_user_by_id(user_id)

    if user is None:
        raise InvalidTokenError()

    return user
