from typing import Annotated

from fastapi import FastAPI, Response, Query, Request
from starlette.responses import RedirectResponse

from src.clients import telegram_web
from src.db.utils import init_db
from src.schemas.web import LoginTelegramParams

app = FastAPI()
Session = init_db()

@app.get("/login/telegram")
async def login_telegram(
    params: Annotated[LoginTelegramParams, Query()],
    response: Response,
) -> RedirectResponse:
    auth_data = telegram_web.check_telegram_authorization(auth_data=params)
    response.set_cookie(key="tg_user", value=auth_data.json())

    return RedirectResponse("/")


@app.get("/")
async def root(request: Request):
    return {"tg_user": request.cookies.get('tg_user')}