from uuid import UUID

from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import models, get_async_session


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
