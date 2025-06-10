import datetime
import logging

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from telegram import Bot

from src.clients import shikimori
from src.clients.manga import MangaUpdatesClient
from src.config import Config
from src.db import models, enums
from src.jobs.run import Session
from src.jobs.utils import periodic_task_run

log = logging.getLogger(__name__)


manga_client = MangaUpdatesClient()


def is_valid_time_for_notification() -> bool:
    return datetime.datetime.now().time() > datetime.time(18, 0)


@periodic_task_run(sleep=Config.NOTIFICATION_PERIOD_ANIME)
async def check_notifications_anime():
    if not is_valid_time_for_notification():
        return

    async with Session() as session:
        query = (
            select(models.Anime)
            .where(
                func.DATE(models.Anime.next_air_at) == datetime.date.today(),
                (
                    (
                        func.DATE(models.Anime.last_notification_at)
                        != datetime.date.today()
                    )
                    | (models.Anime.last_notification_at.is_(None))
                ),
            )
            .options(
                joinedload(models.Anime.subscriptions).joinedload(
                    models.Subscription.user
                )
            )
        )

        animes = (await session.scalars(query)).unique().all()

    for anime in animes:
        async with Session() as session:
            query = (
                select(models.Anime)
                .with_for_update()
                .where(models.Anime.id == anime.id)
            )
            anime_locked = (await session.scalars(query)).one()

            if (
                anime_locked.last_notification_at
                and anime_locked.last_notification_at.date() == datetime.date.today()
            ):
                continue

            shikimori_response = None
            shikimori_anime = None

            try:
                shikimori_response = await shikimori.send_shikimori(
                    ids=[anime.external_id]
                )
            except Exception:
                log.exception('Ошибка при запросе в шикимори anime_id=%s', anime.id)

            if shikimori_response:
                try:
                    shikimori_anime = shikimori_response['animes'][0]
                except KeyError:
                    log.error('Ошибка в ответе шикимори: %s', shikimori_response)

                if shikimori_anime:
                    anime_locked.next_air_at = datetime.datetime.fromisoformat(
                        shikimori_anime['nextEpisodeAt']
                    )
                    anime_locked.episodes_aired = shikimori_anime['episodesAired']
                    anime_locked.episodes_number = shikimori_anime['episodes']

            anime_locked.last_notification_at = datetime.datetime.now()
            await session.commit()

        for subscription in anime.subscriptions:
            await _send_telegram_message(
                user_id=subscription.user.telegram_id,
                text=f'Вышла новая серия аниме: {anime.name}\n{anime.site_url}',
                photo=anime.image_url,
            )


@periodic_task_run(sleep=Config.NOTIFICATION_PERIOD_MANGA)
async def check_notifications_manga():
    if not is_valid_time_for_notification():
        return

    async with Session() as session:
        query = (
            select(models.Manga)
            .where(
                models.Manga.status == enums.MangaStatus.airing,
            )
            .options(
                joinedload(models.Manga.subscriptions).joinedload(
                    models.SubscriptionManga.user
                )
            )
        )

        manga_list = (await session.scalars(query)).unique().all()

    for manga in manga_list:
        need_notification = False

        async with Session() as session:
            query = (
                select(models.Manga)
                .with_for_update()
                .where(models.Manga.id == manga.id)
            )
            manga_locked = (await session.scalars(query)).one()

            if manga_locked.status != enums.MangaStatus.airing:
                continue

            try:
                series = await manga_client.get_series(series_id=manga.external_id)
            except Exception:
                log.exception('Ошибка при запросе в MangaUpdate manga_id=%s', manga.id)
                continue

            if series.completed:
                manga_locked.status = enums.MangaStatus.ended

            if manga_locked.latest_chapter < series.latest_chapter:
                manga_locked.last_notification_at = datetime.datetime.now()
                manga_locked.latest_chapter = series.latest_chapter
                need_notification = True

            await session.commit()

        if need_notification:
            for subscription in manga.subscriptions:
                await _send_telegram_message(
                    user_id=subscription.user.telegram_id,
                    text=f'Вышла новая глава манги: {manga.name}\n{manga.site_url}',
                    photo=manga.image_url,
                )


async def _send_telegram_message(user_id: str | int, text: str, photo: str):
    async with Bot(Config.BOT_TOKEN) as bot:
        await bot.send_photo(chat_id=user_id, photo=photo, caption=text)
