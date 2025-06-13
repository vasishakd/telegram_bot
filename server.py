import datetime
import logging
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, Query, Request
from starlette.responses import RedirectResponse, HTMLResponse

from src.clients import telegram_web
from src.clients.telegram_web import TelegramAuthException
from src.db import models
from src.db.utils import init_db
from src.schemas.web import LoginTelegramParams

log = logging.getLogger(__name__)
app = FastAPI()
Session = init_db()

@app.get("/login")
async def login() -> HTMLResponse:
    file = open("resources/index.html", "r")
    content = file.read()
    file.close()

    return HTMLResponse(content=content, status_code=200)


@app.get("/login/telegram")
async def login_telegram(
    params: Annotated[LoginTelegramParams, Query()],
) -> RedirectResponse:
    auth_data = None
    try:
        auth_data = telegram_web.check_telegram_authorization(auth_data=params.model_dump())
    except TelegramAuthException:
        log.exception('Check telegram authorization error')

    if not auth_data:
        return RedirectResponse('/')

    async with Session() as session:
        user, _ = await models.User.get_or_create(
            session=session,
            telegram_id=str(params.id),
            defaults={
                'name': f'{params.first_name} {params.last_name}',
            }
        )
        user_session = await models.UserSession.create(
            session=session,
            user_id=user.id,
            data=auth_data,
            expires_at=datetime.datetime.now() + datetime.timedelta(days=30),
        )

    response = RedirectResponse('/')
    response.set_cookie(
        key='session_id',
        value=str(user_session.id),
        httponly=True,
        # secure=True,
        max_age=60 * 60 * 24 * 30,
        samesite="lax",
    )

    return response


@app.get("/")
async def root(request: Request):
    session_id = request.cookies.get('session_id')

    if not session_id:
        return {'foo': 'bar'}

    async with Session() as session:
        user_session = await models.UserSession.get_session(session=session, session_id=UUID(session_id))

    return {"tg_user": user_session.user.name}