from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src import enums
from src.db import models
from src.db.utils import init_db
from src.utils import require_user_session

router = APIRouter(prefix='/api')
Session = init_db()


@router.get('/subscriptions')
async def subscriptions(
    user_session: Annotated[models.UserSession, Depends(require_user_session)],
):
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
                'type': enums.SubscriptionType.manga,
                'progress': f'{subscription.anime.episodes_aired} episodes',
                'image': subscription.anime.image_url,
            }
        )

    for subscription in subscriptions_manga:
        result.append(
            {
                'id': subscription.id,
                'title': subscription.manga.name,
                'type': enums.SubscriptionType.manga,
                'progress': f'{subscription.manga.latest_chapter} chapters',
                'image': subscription.manga.image_url,
            }
        )

    return result


@router.get('/user')
async def user(
    user_session: Annotated[models.UserSession, Depends(require_user_session)],
):
    return {
        'name': user_session.user.name,
        'image': user_session.user.image_url,
    }


@router.post('/subscriptions/{subscription_type}/{subscription_id}/cancel')
async def cancel(
    subscription_id: int,
    subscription_type: enums.SubscriptionType,
):
    subscription_class = {
        enums.SubscriptionType.anime: models.Subscription,
        enums.SubscriptionType.manga: models.SubscriptionManga,
    }
    async with Session() as session:
        subscription = await subscription_class[subscription_type].get(
            id=subscription_id, session=session
        )
        await subscription.delete(session)

    return True
