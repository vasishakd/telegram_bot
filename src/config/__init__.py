import logging
import sys

from dotenv import dotenv_values
from pydantic import BaseModel, Field
import pathlib


class ConfigENV(BaseModel):
    DB_HOST: str
    DB_PASS: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    BOT_TOKEN: str
    ADMIN_SESSION_ID: str | None = Field(default=None)
    LOG_LEVEL: str = Field(default='DEBUG')
    NOTIFICATION_PERIOD_ANIME: int | None = Field(default=60 * 15)
    NOTIFICATION_PERIOD_MANGA: int | None = Field(default=60 * 60)
    MANGA_UPDATES_URL: str | None = Field(default='https://api.mangaupdates.com/')


paths = pathlib.Path(__file__).parent.resolve()


Config = ConfigENV(
    **dotenv_values(pathlib.Path(__file__).parent.resolve() / '../../.env')
)

logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
