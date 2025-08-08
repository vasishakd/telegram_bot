import dataclasses
import typing

from pydantic import BaseModel, model_validator

from src.clients.base import JsonBaseClient
from src.config import Config
from src.enums import Currency


class SeriesBase(BaseModel):
    title: str
    series_id: int
    url: str
    year: str
    image_url: str | None

    @model_validator(mode='before')
    @classmethod
    def handle_image_url(cls, data: dict) -> dict:
        data['image_url'] = data['image']['url']['original']

        return data


class ExchangeResponseSuccess(BaseModel):
    result: str
    time_last_update_unix: int
    time_next_update_unix: int
    base_code: str
    conversion_rates: dict


class ExchangeResponseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


@dataclasses.dataclass
class CurrencyExchangeClient(JsonBaseClient):
    base_url: str = Config.CURRENCY_EXCHANGE_URL

    async def request(
        self,
        method: str,
        path: typing.Optional[str] = None,
        **params,
    ):
        return await super().request(
            method=method,
            path=f'{Config.CURRENCY_EXCHANGE_API_KEY}/{path}',
            **params,
        )

    async def get_exchange(
        self, currency: Currency
    ) -> ExchangeResponseSuccess | ExchangeResponseError:
        response = await self.get(f'latest/{currency}')

        if response['result'] == 'error':
            return ExchangeResponseError(response['error-type'])

        return ExchangeResponseSuccess(**response)
