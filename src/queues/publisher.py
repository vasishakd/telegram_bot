import json

import aio_pika

from src import context


async def publish_message(message: dict, exchange_name: str) -> None:
    rabbitmq_client = context.rabbitmq_client.get()

    exchange = await rabbitmq_client.get_exchange(exchange_name)

    await exchange.publish(
        routing_key=exchange_name,
        message=aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
    )
