from pydantic import BaseModel


class LoginTelegramParams(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    photo_url: str
    auth_date: int
    hash: str
