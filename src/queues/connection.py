import asyncio
from functools import cached_property
from typing import Any
from typing import Optional

import aio_pika
import yarl
from aio_pika.abc import AbstractChannel
from aio_pika.abc import AbstractConnection
from aio_pika.abc import AbstractExchange
from aio_pika.abc import AbstractQueue

ConsumerTag = aio_pika.queue.ConsumerTag
ConnectionPool = aio_pika.pool.Pool[aio_pika.Connection]
ChannelPool = aio_pika.pool.Pool[aio_pika.Channel]

RABBITMQ_SCHEME = 'amqp'
RABBITMQ_PORT = 5672
RABBITMQ_MAX_CONNECTIONS = 3
RABBITMQ_MAX_CHANNELS = 6
RABBITMQ_VHOST = '/'


class RabbitmqClient:
    def __init__(
        self,
        dsn: str,
        max_connections: int = RABBITMQ_MAX_CONNECTIONS,
        max_channels: int = RABBITMQ_MAX_CHANNELS,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._connection_string = dsn
        self._max_connections = max_connections
        self._max_channels = max_channels
        self._loop = loop or asyncio.get_event_loop()

    @classmethod
    def from_params(
        cls,
        host: str,
        login: str,
        password: str,
        scheme: str = RABBITMQ_SCHEME,
        port: int = RABBITMQ_PORT,
        vhost: str = RABBITMQ_VHOST,
        max_connections: int = RABBITMQ_MAX_CONNECTIONS,
        max_channels: int = RABBITMQ_MAX_CHANNELS,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> 'RabbitmqClient':
        dsn = yarl.URL.build(
            scheme=scheme,
            user=login,
            password=password,
            host=host,
            port=port,
            path=vhost,
        )
        return cls(
            dsn=str(dsn),
            max_connections=max_connections,
            max_channels=max_channels,
            loop=loop,
        )

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @cached_property
    def connection_pool(self) -> ConnectionPool:
        return aio_pika.pool.Pool(
            constructor=self.get_connection,
            max_size=self._max_connections,
            loop=self.loop,
        )

    @cached_property
    def channel_pool(self) -> ChannelPool:
        return aio_pika.pool.Pool(
            constructor=self.get_channel,
            max_size=self._max_channels,
            loop=self.loop,
        )

    async def get_connection(self) -> AbstractConnection:
        return await aio_pika.connect_robust(url=str(self._connection_string))

    async def get_channel(self) -> AbstractChannel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel(publisher_confirms=True)

    async def __aenter__(self) -> 'RabbitmqClient':
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    async def declare_exchange(
        self, exchange_name: str, *args: Any, **kwargs: Any
    ) -> AbstractExchange:
        async with self.channel_pool.acquire() as channel:
            return await channel.declare_exchange(exchange_name, *args, **kwargs)

    async def get_exchange(
        self, exchange_name: str, *args: Any, **kwargs: Any
    ) -> AbstractExchange:
        async with self.channel_pool.acquire() as channel:
            return await channel.get_exchange(exchange_name, *args, **kwargs)

    async def declare_queue(
        self,
        queue_name: str,
        prefetch_count: int = 0,
        **kwargs: Any,
    ) -> AbstractQueue:
        channel = await self.get_channel()
        # Установим prefetch_count
        await channel.set_qos(prefetch_count=prefetch_count)

        return await channel.declare_queue(queue_name, **kwargs)

    async def get_queue(
        self,
        queue_name: str,
        prefetch_count: int = 0,
    ) -> AbstractQueue:
        channel = await self.get_channel()
        # Установим prefetch_count
        await channel.set_qos(prefetch_count=prefetch_count)

        return await channel.get_queue(queue_name)

    async def stop(self) -> None:
        await self.channel_pool.close()
        await self.connection_pool.close()
        del self.channel_pool  # noqa
        del self.connection_pool  # noqa
