import typing

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
    NOTIFICATION_PERIOD: typing.Optional[int] = Field(default=300)


paths = pathlib.Path(__file__).parent.resolve()


Config = ConfigENV(**dotenv_values(pathlib.Path(__file__).parent.resolve() / "../.env"))
