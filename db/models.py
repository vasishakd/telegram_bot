from collections.abc import Sequence
from datetime import datetime
from typing import TypeVar

from sqlalchemy import ForeignKey, DateTime, Integer, select, func, UniqueConstraint, Text
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

T = TypeVar('T', bound='BaseModel')


class Base(DeclarativeBase):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    async def get_or_create(cls, session: AsyncSession, defaults: dict = None, **kwargs) -> tuple[T, bool]:
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
    async def get(cls, session: AsyncSession, **kwargs) -> T:
        query = select(cls).filter_by(**kwargs)

        result = await session.scalars(query)
        return result.one()

    @classmethod
    async def get_or_none(cls, session: AsyncSession, **kwargs) -> T:
        query = select(cls).filter_by(**kwargs)

        result = await session.scalars(query)
        return result.one_or_none()

    async def delete(self, session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(), unique=True)
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")


class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))
    anime: Mapped["Anime"] = relationship(back_populates="subscriptions")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="subscriptions")

    __table_args__ = (
        UniqueConstraint('anime_id', 'user_id', name='_anime_user_uc'),
    )

    @classmethod
    async def list_by_user_id(cls, session: AsyncSession, user_id: str) -> Sequence['Subscription']:
        query = (
            select(cls)
            .join(cls.user)
            .where(User.telegram_id == user_id)
        )

        result = await session.scalars(query)

        return result.all()


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    image_url: Mapped[str] = mapped_column(Text(), nullable=True)
    site_url: Mapped[str] = mapped_column(Text(), nullable=True)
    external_id: Mapped[str] = mapped_column(String(), unique=True)
    next_air_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    episodes_number: Mapped[int] = mapped_column(Integer())
    episodes_aired: Mapped[int] = mapped_column(Integer())
    last_notification_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="anime")

