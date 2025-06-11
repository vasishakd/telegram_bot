import datetime
import json
import logging
from enum import StrEnum

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    Application,
)

from src.clients.manga import MangaUpdatesClient
from src.clients.shikimori import send_shikimori
from src.config import Config
from src.db import models, enums
from src.db.utils import init_db

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

WAITING_FOR_TEXT = 1
WAITING_FOR_APPROVE = 2

Session = init_db()
manga_client = MangaUpdatesClient()


class Anime(BaseModel):
    id: str
    image_url: str
    name: str
    name_russian: str
    year: str | int | None
    site_url: str
    episodes_aired: int
    episodes: int
    next_episode_at: str | None


class SubscriptionType(StrEnum):
    manga = 'MANGA'
    anime = 'ANIME'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Выберите команду из списка')


async def subscribe_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Пожалуйста, введите название аниме:')
    return WAITING_FOR_TEXT


async def subscribe_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Пожалуйста, введите название манги:')
    return WAITING_FOR_TEXT


async def handle_text_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    animes = []

    shikimori_response = await send_shikimori(text=user_text, limit=6)

    if not shikimori_response['animes']:
        await update.message.reply_text(
            'Не получилось найти аниме, попробуйте команду /subscribe_anime еще раз'
        )
        return ConversationHandler.END

    for anime in shikimori_response['animes']:
        animes.append(
            Anime(
                id=anime['id'],
                image_url=anime['poster']['originalUrl'],
                name=anime['name'],
                name_russian=anime['russian'],
                year=anime['airedOn']['year'],
                site_url=anime['url'],
                episodes_aired=anime['episodesAired'],
                episodes=anime['episodes'],
                next_episode_at=anime['nextEpisodeAt'],
            )
        )

    context.chat_data['animes'] = animes
    context.chat_data['anime_index'] = 0

    # Создаем кнопки
    keyboard = [
        [
            InlineKeyboardButton('Найти еще', callback_data='find_more_anime'),
            InlineKeyboardButton('Подтвердить', callback_data='confirm_anime'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    anime = animes[0]

    # Отправляем изображение с текстом и кнопками
    await update.message.reply_photo(
        photo=anime.image_url,
        caption=f'Название: {anime.name}/{anime.name_russian}\nГод выпуска: {anime.year}\nСсылка на сайт: {anime.site_url}',
        reply_markup=reply_markup,
    )

    return WAITING_FOR_APPROVE


async def handle_text_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    search_response = await manga_client.search_series(search_text=user_text)

    if not search_response.results:
        await update.message.reply_text(
            'Не получилось найти мангу, попробуйте команду /subscribe_manga еще раз'
        )
        return ConversationHandler.END

    context.chat_data['manga_list'] = search_response.results
    context.chat_data['manga_index'] = 0

    # Создаем кнопки
    keyboard = [
        [
            InlineKeyboardButton('Найти еще', callback_data='find_more_manga'),
            InlineKeyboardButton('Подтвердить', callback_data='confirm_manga'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    manga = search_response.results[0]

    # Отправляем изображение с текстом и кнопками
    await update.message.reply_photo(
        photo=manga.record.image_url,
        caption=f'Название: {manga.record.title}\nГод выпуска: {manga.record.year}\nСсылка на сайт: {manga.record.url}',
        reply_markup=reply_markup,
    )

    return WAITING_FOR_APPROVE


async def find_more_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Создаем кнопки
    keyboard = [
        [
            InlineKeyboardButton('Найти еще', callback_data='find_more_anime'),
            InlineKeyboardButton('Подтвердить', callback_data='confirm_anime'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    anime_index = context.chat_data.get('anime_index') + 1
    context.chat_data['anime_index'] = anime_index

    try:
        anime = context.chat_data.get('animes')[anime_index]
    except IndexError:
        await query.message.reply_text(
            'Не получилось найти аниме, попробуйте еще команду /subscribe_anime еще раз'
        )
        return ConversationHandler.END

    # Отправляем изображение с текстом и кнопками
    await query.message.reply_photo(
        photo=anime.image_url,
        caption=f'Название: {anime.name}/{anime.name_russian}\nГод выпуска: {anime.year}\nСсылка на сайт: {anime.site_url}',
        reply_markup=reply_markup,
    )

    return WAITING_FOR_APPROVE


async def find_more_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Создаем кнопки
    keyboard = [
        [
            InlineKeyboardButton('Найти еще', callback_data='find_more_manga'),
            InlineKeyboardButton('Подтвердить', callback_data='confirm_manga'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    manga_index = context.chat_data.get('manga_index') + 1
    context.chat_data['manga_index'] = manga_index

    try:
        manga = context.chat_data.get('manga_list')[manga_index]
    except IndexError:
        await query.message.reply_text(
            'Не получилось найти аниме, попробуйте еще команду /subscribe_manga еще раз'
        )
        return ConversationHandler.END

    # Отправляем изображение с текстом и кнопками
    await query.message.reply_photo(
        photo=manga.record.image_url,
        caption=f'Название: {manga.record.title}\nГод выпуска: {manga.record.year}\nСсылка на сайт: {manga.record.url}',
        reply_markup=reply_markup,
    )

    return WAITING_FOR_APPROVE


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = json.loads(query.data)

    async with Session() as session:
        if data['type'] == SubscriptionType.anime:
            return await unsubscribe_anime(query=query, session=session, data=data)

        return await unsubscribe_manga(query=query, session=session, data=data)


async def unsubscribe_anime(query: CallbackQuery, session: AsyncSession, data: dict):
    subscription = await models.Subscription.get_or_none(
        session=session, id=int(data['subscription_id'])
    )

    if not subscription:
        await query.message.reply_text('Вы не подписаны на данное аниме')
        return

    anime = await models.Anime.get(session=session, id=subscription.anime_id)
    await subscription.delete(session=session)

    await query.message.reply_text(f'Подписка на аниме ({anime.name}) отменена')


async def unsubscribe_manga(query: CallbackQuery, session: AsyncSession, data: dict):
    subscription = await models.SubscriptionManga.get_or_none(
        session=session, id=int(data['subscription_id'])
    )

    if not subscription:
        await query.message.reply_text('Вы не подписаны эту мангу')
        return

    manga = await models.Manga.get(session=session, id=subscription.manga_id)
    await subscription.delete(session=session)

    await query.message.reply_text(f'Подписка на мангу ({manga.name}) отменена')


async def subscriptions_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with Session() as session:
        subscriptions_list = await models.Subscription.list_by_user_id(
            session=session, user_id=str(update.message.from_user.id)
        )

        if not subscriptions_list:
            await update.message.reply_text(
                'У вас нет активных подписок, чтобы подписаться на новые серии используйте команду /subscribe_anime'
            )
            return ConversationHandler.END

        for subscription in subscriptions_list:
            callback_data = {
                'subscription_id': subscription.id,
                'action': 'unsubscribe',
                'type': SubscriptionType.anime,
            }
            keyboard = [
                [
                    InlineKeyboardButton(
                        'Отписаться', callback_data=json.dumps(callback_data)
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            anime = await models.Anime.get(session=session, id=subscription.anime_id)

            await update.message.reply_photo(
                photo=anime.image_url,
                caption=f'Название: {anime.name}\nСсылка на сайт: {anime.site_url}',
                reply_markup=reply_markup,
            )


async def subscriptions_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with Session() as session:
        subscriptions_list = await models.SubscriptionManga.list_by_user_id(
            session=session, user_id=str(update.message.from_user.id)
        )

        if not subscriptions_list:
            await update.message.reply_text(
                'У вас нет активных подписок, чтобы подписаться на мангу используйте команду /subscribe_manga'
            )
            return ConversationHandler.END

        for subscription in subscriptions_list:
            callback_data = {
                'subscription_id': subscription.id,
                'action': 'unsubscribe',
                'type': SubscriptionType.manga,
            }
            keyboard = [
                [
                    InlineKeyboardButton(
                        'Отписаться', callback_data=json.dumps(callback_data)
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            manga: models.Manga = await models.Manga.get(
                session=session, id=subscription.manga_id
            )

            await update.message.reply_photo(
                photo=manga.image_url,
                caption=f'Название: {manga.name}\nСсылка на сайт: {manga.site_url}',
                reply_markup=reply_markup,
            )


async def confirm_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    anime_index = context.chat_data.get('anime_index')
    anime: Anime = context.chat_data.get('animes')[anime_index]

    async with Session() as session:
        user, _ = await models.User.get_or_create(
            session=session, telegram_id=str(query.from_user.id)
        )
        anime_model, _ = await models.Anime.get_or_create(
            session=session,
            external_id=anime.id,
            defaults={
                'name': f'{anime.name} / {anime.name_russian}',
                'next_air_at': datetime.datetime.fromisoformat(anime.next_episode_at)
                if anime.next_episode_at
                else None,
                'episodes_number': anime.episodes,
                'episodes_aired': anime.episodes_aired,
                'last_notification_at': None,
                'image_url': anime.image_url,
                'site_url': anime.site_url,
            },
        )
        subscription, new_subscription = await models.Subscription.get_or_create(
            session=session,
            anime_id=anime_model.id,
            user_id=user.id,
        )

    await query.message.reply_text(
        'Подписка на уведомления оформлена!'
        if new_subscription
        else 'Вы уже подписаны на это аниме'
    )
    return ConversationHandler.END


async def confirm_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    manga_index = context.chat_data.get('manga_index')
    manga = context.chat_data.get('manga_list')[manga_index]
    manga = await manga_client.get_series(series_id=manga.record.series_id)

    async with Session() as session:
        user, _ = await models.User.get_or_create(
            session=session, telegram_id=str(query.from_user.id)
        )
        manga_model, _ = await models.Manga.get_or_create(
            session=session,
            external_id=str(manga.series_id),
            defaults={
                'name': manga.title,
                'latest_chapter': manga.latest_chapter,
                'last_notification_at': None,
                'image_url': manga.image_url,
                'site_url': manga.url,
                'status': enums.MangaStatus.ended
                if manga.completed
                else enums.MangaStatus.airing,
            },
        )
        subscription, new_subscription = await models.SubscriptionManga.get_or_create(
            session=session,
            manga_id=manga_model.id,
            user_id=user.id,
        )

    await query.message.reply_text(
        'Подписка на уведомления оформлена!'
        if new_subscription
        else 'Вы уже подписаны на эту мангу'
    )
    return ConversationHandler.END


async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands(
        [
            ('start', 'Starts the bot'),
            ('subscribe_anime', 'Подписаться на уведомления Аниме'),
            ('subscribe_manga', 'Подписаться на уведомления по манге'),
            ('subscriptions_anime', 'Посмотреть текущие подписки на аниме'),
            ('subscriptions_manga', 'Посмотреть текущие подписки на мангу'),
            ('cancel', 'Отменить текущую команду'),
        ]
    )
    await app.bot.set_chat_menu_button()


def main():
    TOKEN = Config.BOT_TOKEN

    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('subscriptions_anime', subscriptions_anime))
    app.add_handler(CommandHandler('subscriptions_manga', subscriptions_manga))
    app.add_handler(CallbackQueryHandler(unsubscribe, pattern='.*unsubscribe.*'))

    subscribe_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe_anime', subscribe_anime)],
        states={
            WAITING_FOR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_anime)
            ],
            WAITING_FOR_APPROVE: [
                CallbackQueryHandler(find_more_anime, pattern='^find_more_anime$'),
                CallbackQueryHandler(confirm_anime, pattern='^confirm_anime$'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_conversation, pattern='^env_conversation$'),
            CommandHandler('cancel', end_conversation),
        ],
    )
    app.add_handler(subscribe_handler)

    subscribe_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe_manga', subscribe_manga)],
        states={
            WAITING_FOR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_manga)
            ],
            WAITING_FOR_APPROVE: [
                CallbackQueryHandler(find_more_manga, pattern='^find_more_manga$'),
                CallbackQueryHandler(confirm_manga, pattern='^confirm_manga$'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_conversation, pattern='^env_conversation$'),
            CommandHandler('cancel', end_conversation),
        ],
    )
    app.add_handler(subscribe_handler)

    print('Бот запущен')
    app.run_polling()


if __name__ == '__main__':
    main()
