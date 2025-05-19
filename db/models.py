from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Integer, select, func, UniqueConstraint, Text
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    async def get_or_create(cls, session: AsyncSession, defaults: dict = None, **kwargs) -> tuple['Base', bool]:
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


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    image_url: Mapped[str] = mapped_column(Text(), nullable=True)
    site_url: Mapped[str] = mapped_column(Text(), nullable=True)
    external_id: Mapped[str] = mapped_column(String(), unique=True)
    next_air_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    episodes_number: Mapped[int] = mapped_column(Integer())
    episodes_aired: Mapped[int] = mapped_column(Integer())
    last_notification_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="anime")

