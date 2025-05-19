import datetime
import logging

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from telegram import Bot

from config import Config
from db import models
from jobs.run import Session
from jobs.utils import periodic_task_run

log = logging.getLogger(__name__)


@periodic_task_run(sleep=Config.NOTIFICATION_PERIOD)
async def check_notifications():
    async with Session() as session:
        query = (
            select(models.Anime)
            .where(
                func.DATE(models.Anime.next_air_at) == datetime.date.today(),
                func.DATE(models.Anime.last_notification_at) != datetime.date.today(),
            )
            .options(joinedload(models.Anime.subscriptions).joinedload(models.Subscription.user))
        )

        animes = (await session.scalars(query)).unique().all()

        for anime in animes:
            anime.last_notification_at = datetime.datetime.now()

        await session.commit()

    for anime in animes:
        for subscription in anime.subscriptions:
            await _send_telegram_message(
                user_id=subscription.user.telegram_id,
                text=f'Вышла новая серия аниме: {anime.name}\n{anime.site_url}',
                photo=anime.image_url,
            )


async def _send_telegram_message(user_id: str | int, text: str, photo: str):
    async with Bot(Config.BOT_TOKEN) as bot:
        await bot.send_photo(chat_id=user_id, photo=photo, caption=text)
