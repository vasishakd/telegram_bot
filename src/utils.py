from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import models


async def get_user_session(session: AsyncSession, request: Request):
    session_id = request.cookies.get('session_id')

    if not session_id:
        return None

    return await models.UserSession.get_session(
        session=session, session_id=UUID(session_id)
    )
