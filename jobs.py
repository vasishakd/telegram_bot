import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.jobs import tasks

log = logging.getLogger(__name__)


tasks_list = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info('🔄 Starting background tasks')

    tasks_list.append(asyncio.create_task(tasks.check_notifications_anime()))
    tasks_list.append(asyncio.create_task(tasks.check_notifications_manga()))

    yield  # run app

    log.info('🛑 Shutting down background tasks')
    for task in tasks_list:
        task.cancel()


# Create app
app = FastAPI(lifespan=lifespan)


@app.get('/health')
async def root():
    return {'status': 'Fok'}
