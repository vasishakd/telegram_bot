from fastapi import APIRouter, Depends

from src import constants
from src.db import models, Session
from src.enums import Currency
from src.jobs import service

from src.utils import verify_basic_auth

router = APIRouter(prefix='/api/currency')


@router.get('/exchange-rates')
async def rates():
    async with Session() as session:
        currency_exchanges = await models.CurrencyExchange.get_latest_list(
            session=session
        )

    return {
        currency_exchange.currency: currency_exchange.rates
        for currency_exchange in currency_exchanges
    }


@router.get('/list')
async def list_currencies():
    data = {}
    for currency in Currency.active_currencies():
        if (
            currency not in constants.CURRENCY_SYMBOLS.keys()
            or currency not in constants.CURRENCY_FLAG.keys()
        ):
            continue

        data[currency] = {
            'symbol': constants.CURRENCY_SYMBOLS[currency],
            'name': currency.full_name,
            'flag': constants.CURRENCY_FLAG[currency],
        }

    return data


@router.get('/refresh', dependencies=[Depends(verify_basic_auth)])
async def refresh_currencies():
    await service.refresh_currency_rates()
