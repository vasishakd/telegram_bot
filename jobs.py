import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.jobs import tasks

log = logging.getLogger(__name__)


tasks_list = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.debug('🔄 Starting background tasks')

    app.state._tasks = [
        asyncio.create_task(tasks.check_notifications_anime()),
        asyncio.create_task(tasks.check_notifications_manga()),
    ]

    yield  # run app

    log.debug(f'Shutting down background tasks {app.state._tasks}')
    for task in app.state._tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            log.debug('Task cancelled cleanly')


# Create app
app = FastAPI(lifespan=lifespan)


@app.get('/health')
async def root():
    return {'status': 'Fok'}
