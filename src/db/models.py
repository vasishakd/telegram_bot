from collections.abc import Sequence
from datetime import datetime
from typing import Type, Self
from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    DateTime,
    Integer,
    select,
    func,
    UniqueConstraint,
    Text,
    TIMESTAMP,
)
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, joinedload
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.db import enums


class Base(DeclarativeBase):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    async def get_or_create(
        cls: Type[Self], session: AsyncSession, defaults: dict = None, **kwargs
    ) -> tuple[Self, bool]:
        query = select(cls).filter_by(**kwargs)

        result = await session.scalars(query)
        result = result.one_or_none()

        if result:
            return result, False

        data = {**kwargs}
        if defaults:
            data.update(defaults)

        result = cls(**data)

        session.add(result)
        await session.commit()

        return result, True

    @classmethod
    async def get(cls: Type[Self], session: AsyncSession, **kwargs) -> Self:
        query = select(cls).filter_by(**kwargs)

        result = await session.scalars(query)
        return result.one()

    @classmethod
    async def get_or_none(
        cls: Type[Self], session: AsyncSession, **kwargs
    ) -> Self | None:
        query = select(cls).filter_by(**kwargs)

        result = await session.scalars(query)
        return result.one_or_none()

    async def delete(self: Type[Self], session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()

    @classmethod
    async def create(cls: Type[Self], session: AsyncSession, **kwargs) -> Self:
        result = cls(**kwargs)

        session.add(result)
        await session.commit()

        return result


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=True)
    telegram_id: Mapped[str] = mapped_column(String(), unique=True)
    subscriptions: Mapped[list['Subscription']] = relationship(back_populates='user')
    subscriptions_manga: Mapped[list['SubscriptionManga']] = relationship(
        back_populates='user'
    )
    sessions: Mapped[list['UserSession']] = relationship(back_populates='user')
    image_url: Mapped[str] = mapped_column(Text(), nullable=True)


class Subscription(Base):
    __tablename__ = 'subscription'

    id: Mapped[int] = mapped_column(primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey('anime.id'))
    anime: Mapped['Anime'] = relationship(back_populates='subscriptions')
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='subscriptions')

    __table_args__ = (UniqueConstraint('anime_id', 'user_id', name='_anime_user_uc'),)

    @classmethod
    async def list_by_user_id(
        cls, session: AsyncSession, user_id: str
    ) -> Sequence['Subscription']:
        query = (
            select(cls)
            .join(cls.user)
            .where(User.telegram_id == user_id)
            .options(joinedload(cls.anime))
        )
        result = await session.scalars(query)

        return result.all()


class SubscriptionManga(Base):
    __tablename__ = 'subscriptionmanga'

    id: Mapped[int] = mapped_column(primary_key=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey('manga.id'))
    manga: Mapped['Manga'] = relationship(back_populates='subscriptions')
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='subscriptions_manga')

    __table_args__ = (UniqueConstraint('manga_id', 'user_id', name='_manga_user_uc'),)

    @classmethod
    async def list_by_user_id(
        cls, session: AsyncSession, user_id: str
    ) -> Sequence['SubscriptionManga']:
        query = (
            select(cls)
            .join(cls.user)
            .where(User.telegram_id == user_id)
            .options(joinedload(cls.manga))
        )
        result = await session.scalars(query)

        return result.all()


class Anime(Base):
    __tablename__ = 'anime'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    image_url: Mapped[str] = mapped_column(Text(), nullable=True)
    site_url: Mapped[str] = mapped_column(Text(), nullable=True)
    external_id: Mapped[str] = mapped_column(String(), unique=True)
    next_air_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    episodes_number: Mapped[int] = mapped_column(Integer())
    episodes_aired: Mapped[int] = mapped_column(Integer())
    last_notification_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    subscriptions: Mapped[list['Subscription']] = relationship(back_populates='anime')


class Manga(Base):
    __tablename__ = 'manga'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    image_url: Mapped[str] = mapped_column(Text(), nullable=True)
    site_url: Mapped[str] = mapped_column(Text(), nullable=True)
    external_id: Mapped[str] = mapped_column(String(), unique=True)
    latest_chapter: Mapped[int] = mapped_column(Integer())
    last_notification_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    subscriptions: Mapped[list['SubscriptionManga']] = relationship(
        back_populates='manga'
    )
    status: Mapped[enums.MangaStatus] = mapped_column(
        String(), default=enums.MangaStatus.airing
    )


class UserSession(Base):
    __tablename__ = 'usersession'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='sessions')
    data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    @classmethod
    async def get_session(cls, session: AsyncSession, session_id: UUID):
        query = (
            select(cls)
            .where(cls.id == session_id)
            .options(joinedload(cls.user))
            .order_by(cls.created_at.desc())
        )
        session_obj = (await session.scalars(query)).one_or_none()

        if session_obj and session_obj.expires_at > datetime.now():
            return session_obj
        return None
