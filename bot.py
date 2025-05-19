import datetime
import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from pydantic import BaseModel
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, \
    filters, ConversationHandler, Application

from config import Config
from db import models
from db.utils import init_db

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

WAITING_FOR_TEXT = 1
WAITING_FOR_APPROVE = 2

Session = init_db()


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Используйте команду /subscribe для подписки.")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, введите название аниме:")
    return WAITING_FOR_TEXT


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    animes = []

    shikimori_response = await send_shikimori(user_text)

    if not shikimori_response['animes']:
        await update.message.reply_text('Не получилось найти аниме, попробуйте еще команду /subsсribe еще раз')
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
            InlineKeyboardButton("Найти еще", callback_data='find_more'),
            InlineKeyboardButton("Подтвердить", callback_data='confirm')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    anime = animes[0]

    # Отправляем изображение с текстом и кнопками
    await update.message.reply_photo(
        photo=anime.image_url,
        caption=f"Название: {anime.name}/{anime.name_russian}\nГод выпуска: {anime.year}\nСсылка на сайт: {anime.site_url}",
        reply_markup=reply_markup,
    )

    return WAITING_FOR_APPROVE


async def find_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Создаем кнопки
    keyboard = [
        [
            InlineKeyboardButton("Найти еще", callback_data='find_more'),
            InlineKeyboardButton("Подтвердить", callback_data='confirm')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    anime_index = context.chat_data.get('anime_index') + 1
    context.chat_data['anime_index'] = anime_index

    try:
        anime = context.chat_data.get('animes')[anime_index]
    except IndexError:
        await query.message.reply_text('Не получилось найти аниме, попробуйте еще команду /subsсribe еще раз')
        return ConversationHandler.END

    # Отправляем изображение с текстом и кнопками
    await query.message.reply_photo(
        photo=anime.image_url,
        caption=f"Название: {anime.name}/{anime.name_russian}\nГод выпуска: {anime.year}\nСсылка на сайт: {anime.site_url}",
        reply_markup=reply_markup,
    )

    return WAITING_FOR_APPROVE


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    anime_index = context.chat_data.get('anime_index')
    anime: Anime = context.chat_data.get('animes')[anime_index]

    async with Session() as session:
        user, _ = await models.User.get_or_create(session=session, telegram_id=str(query.from_user.id))
        anime_model, _ = await models.Anime.get_or_create(
            session=session,
            external_id=anime.id,
            defaults={
                'name': f'{anime.name} / {anime.name_russian}',
                'next_air_at': datetime.datetime.fromisoformat(anime.next_episode_at),
                'episodes_number': anime.episodes,
                'episodes_aired': anime.episodes_aired,
                'last_notification_at': datetime.datetime.now(),
                'image_url': anime.image_url,
                'site_url': anime.site_url,
            }

        )
        subscription, new_subscription = await models.Subscription.get_or_create(
            session=session,
            anime_id=anime_model.id,
            user_id=user.id,
        )

    await query.message.reply_text("Подписка на уведомления оформлена!" if new_subscription else "Вы уже подписаны на это аниме")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Подписка отменена.")
    return ConversationHandler.END


async def send_shikimori(text: str):
    transport = AIOHTTPTransport(url="https://shikimori.one/api/graphql")

    # Using `async with` on the client will start a connection on the transport
    # and provide a `session` variable to execute queries on this connection
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        # Execute single query
        query = gql(
            f"""
                {{
                  animes(search: "{text}", limit: 6) {{
                    id
                    malId
                    name
                    russian
                    licenseNameRu
                    english
                    japanese
                    synonyms
                    kind
                    rating
                    score
                    status
                    episodes
                    episodesAired
                    duration
                    airedOn {{ year month day date }}
                    releasedOn {{ year month day date }}
                    url
                    season

                    poster {{ id originalUrl mainUrl }}

                    fansubbers
                    fandubbers
                    licensors
                    createdAt,
                    updatedAt,
                    nextEpisodeAt,
                    isCensored
                  }}
                }}
                """
        )

        return await session.execute(query)


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands([('start', 'Starts the bot'), ('subscribe', 'Подписаться на уведомления Аниме')])
    await app.bot.set_chat_menu_button()


def main():
    TOKEN = Config.BOT_TOKEN

    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', subscribe)],
        states={
            WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            WAITING_FOR_APPROVE: [
                CallbackQueryHandler(find_more, pattern="^find_more"),
                CallbackQueryHandler(confirm, pattern="^confirm$"),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conv_handler)

    print("Бот запущен")
    app.run_polling()


if __name__ == '__main__':
    main()
