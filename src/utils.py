from uuid import UUID

from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Config
from src.db import models, get_async_session

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()


async def get_user_session(
    session: AsyncSession, request: Request
) -> models.UserSession | None:
    session_id = request.cookies.get('session_id')

    if not session_id:
        return None

    return await models.UserSession.get_session(
        session=session, session_id=UUID(session_id)
    )


async def require_user_session(
    request: Request, session: AsyncSession = Depends(get_async_session)
) -> models.UserSession:
    user_session = await get_user_session(session, request)

    if not user_session:
        raise HTTPException(status_code=403, detail='Forbidden')

    return user_session


def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    is_username_valid = secrets.compare_digest(
        credentials.username,
        Config.BASIC_AUTH_LOGIN,
    )
    is_password_valid = secrets.compare_digest(
        credentials.password,
        Config.BASIC_AUTH_PASSWORD,
    )

    if not (is_username_valid and is_password_valid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Basic'},
        )

    return credentials.username
