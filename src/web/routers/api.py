from fastapi import APIRouter, HTTPException, Request

from src.db import models
from src.db.utils import init_db
from src.utils import get_user_session

router = APIRouter(prefix='/api')
Session = init_db()


@router.get('/subscriptions')
async def subscriptions(request: Request):
    async with Session() as session:
        user_session = await get_user_session(session=session, request=request)

    if not user_session:
        return HTTPException(status_code=403, detail='Forbidden')

    async with Session() as session:
        subscriptions_anime = await models.Subscription.list_by_user_id(
            session=session, user_id=user_session.user.telegram_id
        )
        subscriptions_manga = await models.SubscriptionManga.list_by_user_id(
            session=session, user_id=user_session.user.telegram_id
        )

    result = []

    for subscription in subscriptions_anime:
        result.append(
            {
                'id': subscription.id,
                'title': subscription.anime.name,
                'type': 'Anime',
                'progress': f'{subscription.anime.episodes_aired} episodes',
                'image': subscription.anime.image_url,
            }
        )

    for subscription in subscriptions_manga:
        result.append(
            {
                'id': subscription.id,
                'title': subscription.manga.name,
                'type': 'Manga',
                'progress': f'{subscription.manga.latest_chapter} chapters',
                'image': subscription.manga.image_url,
            }
        )

    return result
