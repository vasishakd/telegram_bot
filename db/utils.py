from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import Config


def init_db() -> async_sessionmaker:
    engine = create_async_engine(generate_db_url(), echo=True)
    return async_sessionmaker(engine, expire_on_commit=False)


def generate_db_url() -> str:
    return f'postgresql+asyncpg://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}'
