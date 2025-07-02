from contextlib import asynccontextmanager

from fastapi import FastAPI

import asyncio
import json
import logging

from aio_pika.abc import AbstractIncomingMessage, AbstractQueue

from src import context
from src.config import Config
from src.queues.connection import RabbitmqClient
from src.queues.topology import build_queues

EXCHANGE_NAME = 'exchange_1'
log = logging.getLogger(__name__)


async def consume_message(message: AbstractIncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body)
            log.info('Message body %s', payload)
        except Exception as e:
            log.info(f'❌ Failed to process message: {e}')


async def consume(queue: AbstractQueue):
    await queue.consume(consume_message)


async def run_listener(app: FastAPI):
    rabbitmq_client = RabbitmqClient.from_params(
        host=Config.RABBITMQ_HOST,
        port=Config.RABBITMQ_PORT,
        login=Config.RABBITMQ_LOGIN,
        password=Config.RABBITMQ_PASSWORD,
    )
    context.rabbitmq_client.set(rabbitmq_client)

    queues = await build_queues()
    print(queues)
    app.state._queues = queues

    await asyncio.gather(
        *[consume(queue=queue) for queue_name, queue in queues.items()]
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_listener(app)

    yield  # run app

    rabbitmq_client: RabbitmqClient = context.rabbitmq_client.get()
    await rabbitmq_client.stop()


# Create app
app = FastAPI(lifespan=lifespan)


@app.get('/health')
async def root():
    return {'status': 'Fok'}
