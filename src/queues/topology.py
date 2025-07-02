from typing import Optional
from typing import Tuple

import aio_pika
from aio_pika.abc import AbstractExchange
from aio_pika.abc import AbstractQueue

from src import context
from src.queues.connection import RabbitmqClient

DLX_NAME = 'DLX'
DLX_UNKNOWN_NAME = 'DLX.unknown'
MINUTES_MS = 60000


async def _declare_dlx_unknown_queue(
    rabbitmq_client: RabbitmqClient,
) -> None:
    dlx_unknown_exchange = await rabbitmq_client.declare_exchange(
        exchange_name=DLX_UNKNOWN_NAME,
        type=aio_pika.ExchangeType.FANOUT,
        durable=True,
    )
    dlx_unknown_queue = await rabbitmq_client.declare_queue(
        queue_name=DLX_UNKNOWN_NAME,
        durable=True,
    )
    await dlx_unknown_queue.bind(dlx_unknown_exchange)


async def _declare_dlx_exchange(
    rabbitmq_client: RabbitmqClient,
) -> AbstractExchange:
    return await rabbitmq_client.declare_exchange(
        exchange_name=DLX_NAME,
        type=aio_pika.ExchangeType.DIRECT,
        arguments={'alternate-exchange': DLX_UNKNOWN_NAME},
        durable=True,
    )


async def declare_rabbitry_queue(
    queue_name: str,
    rabbitmq_client: RabbitmqClient,
    auto_retry_ms: Optional[int] = None,
    declare_dlx_unknown_queue: bool = False,
    declare_dlx_exchange: bool = False,
    queue_exchange_durable: bool = True,
) -> Tuple[AbstractQueue, AbstractExchange]:
    if declare_dlx_unknown_queue:
        await _declare_dlx_unknown_queue(rabbitmq_client)

    dlx_queue_name = f'DLX.{queue_name}'

    queue = await rabbitmq_client.declare_queue(
        queue_name=queue_name,
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLX_NAME,
            'x-dead-letter-routing-key': dlx_queue_name,
        },
    )

    dlx_queue_arguments = {}

    if auto_retry_ms is not None:
        dlx_queue_arguments.update(
            {
                'x-dead-letter-exchange': queue_name,
                'x-message-ttl': auto_retry_ms,
            }
        )

    dlx_queue = await rabbitmq_client.declare_queue(
        queue_name=dlx_queue_name,
        durable=True,
        arguments=dlx_queue_arguments,
    )

    if declare_dlx_exchange:
        dlx_exchange = await _declare_dlx_exchange(rabbitmq_client)
    else:
        dlx_exchange = await rabbitmq_client.get_exchange(DLX_NAME)

    await dlx_queue.bind(dlx_exchange, routing_key=dlx_queue_name)

    queue_exchange = await rabbitmq_client.declare_exchange(
        exchange_name=queue_name,
        type=aio_pika.ExchangeType.FANOUT,
        durable=queue_exchange_durable,
    )

    await queue.bind(queue_exchange)

    return queue, queue_exchange


async def build_queues() -> dict:
    queues = {}
    rabbitmq_client: RabbitmqClient = context.rabbitmq_client.get()

    for queue_name in ['events']:
        queue, _ = await declare_rabbitry_queue(
            queue_name=queue_name,
            declare_dlx_exchange=True,
            declare_dlx_unknown_queue=True,
            rabbitmq_client=rabbitmq_client,
        )
        queues[queue_name] = queue

    return queues
