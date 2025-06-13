import datetime
import logging
from typing import Annotated

from fastapi import FastAPI, Query, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, FileResponse
from starlette.staticfiles import StaticFiles

from src.clients import telegram_web
from src.clients.telegram_web import TelegramAuthException
from src.db import models
from src.db.utils import init_db
from src.schemas.web import LoginTelegramParams
from src.utils import get_user_session
from src.web.routers import api

log = logging.getLogger(__name__)
Session = init_db()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.mount('/static', StaticFiles(directory='./front/build/static'), name='static')

app.include_router(api.router)


@app.get('/login')
async def login() -> FileResponse:
    return FileResponse('./resources/index.html')


@app.get('/login/telegram')
async def login_telegram(
    params: Annotated[LoginTelegramParams, Query()],
) -> RedirectResponse:
    auth_data = None
    try:
        auth_data = telegram_web.check_telegram_authorization(
            auth_data=params.model_dump()
        )
    except TelegramAuthException:
        log.exception('Check telegram authorization error')

    if not auth_data:
        return RedirectResponse('/login')

    async with Session() as session:
        user, _ = await models.User.get_or_create(
            session=session,
            telegram_id=str(params.id),
            defaults={
                'name': f'{params.first_name} {params.last_name}',
            },
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
        secure=True,
        max_age=60 * 60 * 24 * 30,
        samesite='lax',
    )

    return response


@app.get('/')
async def root(request: Request) -> FileResponse | RedirectResponse:
    async with Session() as session:
        user_session = await get_user_session(request=request, session=session)

    if not user_session:
        return RedirectResponse('/login')

    return FileResponse('./front/build/index.html')
