from sqlalchemy.ext.asyncio import AsyncSession

from src.db.utils import init_db

Session = init_db()


async def get_async_session() -> AsyncSession:
    async with Session() as session:
        yield session
