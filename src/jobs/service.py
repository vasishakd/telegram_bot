import datetime

from sqlalchemy import update

from src.clients.currency import CurrencyExchangeClient
from src.config import Config
from src.db import models, Session
from src.enums import Currency


async def refresh_currency_rates():
    currency_client = CurrencyExchangeClient()

    currency_exchanges = []

    async with Session() as session:
        settings = await models.Settings.get(id=Config.SETTINGS_ID, session=session)

    exchange_rates = await currency_client.get_exchange(currency=Currency.USD)
    last_update_at = datetime.datetime.fromtimestamp(
        exchange_rates.time_last_update_unix
    )
    if last_update_at <= settings.currency_update_at:
        return

    for currency in Currency.active_currencies():
        currency: Currency
        exchange_rates = await currency_client.get_exchange(currency=currency)

        currency_exchanges.append(
            models.CurrencyExchange(
                date_at=datetime.datetime.fromtimestamp(
                    exchange_rates.time_last_update_unix
                ),
                currency=currency,
                rates=exchange_rates.conversion_rates,
            )
        )

    async with Session() as session:
        update_settings_query = (
            update(models.Settings)
            .where(models.Settings.id == Config.SETTINGS_ID)
            .values(currency_update_at=last_update_at)
        )
        await session.execute(update_settings_query)

        session.add_all(currency_exchanges)
        await session.commit()
