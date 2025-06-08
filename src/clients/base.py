import dataclasses
import logging
import typing
from urllib.parse import urljoin

import aiohttp

log = logging.getLogger(__name__)


@dataclasses.dataclass
class BaseClient:
    base_url: str = None
    connector: typing.Callable = dataclasses.field(default=aiohttp.TCPConnector)
    session: typing.Callable = dataclasses.field(default=aiohttp.ClientSession)
    client_timeout_total: int = 30
    client_timeout_connect: int = 5
    base_auth_login: str = dataclasses.field(default=None)
    base_auth_password: str = dataclasses.field(default=None)
    ssl: bool = False
    # Нужно ли закрывать коннект при закрытии сессии
    connector_owner: bool = True
    # Пример переопределения
    # headers: dict = dataclasses.field(default_factory=lambda: {'token': config.CS_ORS_SCORING_TOKEN})
    headers: dict = None
    is_raise_for_status: bool = False

    _session: aiohttp.ClientSession | None = dataclasses.field(default=None, init=False)

    def _get_session(self) -> aiohttp.ClientSession:
        # info
        # при создании экземпляра ClientSession вызывается get_event_loop при этом будет возвращаться текущий луп
        # при этом после может быть переустановка лупа (например uvloop.install()) и если будет вызов будет ошибка
        # Timeout context manager should be used inside a task
        if self._session is None:
            auth = None
            if self.base_auth_login and self.base_auth_password:
                auth = aiohttp.BasicAuth(
                    login=self.base_auth_login, password=self.base_auth_password
                )
            self._session = self.session(
                auth=auth,
                connector=self.connector(ssl=self.ssl),
                timeout=aiohttp.ClientTimeout(
                    total=self.client_timeout_total, connect=self.client_timeout_connect
                ),
                headers=self.headers,
                connector_owner=self.connector_owner,
            )
        return self._session

    @staticmethod
    async def handle_response(response: aiohttp.ClientResponse) -> str:
        return await response.text()

    async def request(
        self,
        method: str,
        path: typing.Optional[str] = None,
        **params,
    ):
        full_url = urljoin(self.base_url, path)

        log.debug('Request: method=%s full_url=%s params=%s', method, full_url, params)

        async with self._get_session().request(
            method=method, url=full_url, **params
        ) as response:
            # Базовый метод после выполнения выходит из контекста менеджера и закрывает соединения
            # и соответственно в месте вызова не получить данные если их не подгрузить заранее
            await response.read()

            if self.is_raise_for_status:
                response.raise_for_status()

            log.debug('Response: %s', (await response.read())[:1000])

            return await self.handle_response(response=response)

    async def get(self, *args, **kwargs):
        return await self.request('GET', *args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self.request('POST', *args, **kwargs)

    async def put(self, *args, **kwargs):
        return await self.request('PUT', *args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await self.request('DELETE', *args, **kwargs)

    async def patch(self, *args, **kwargs):
        return await self.request('PATCH', *args, **kwargs)

    async def head(self, *args, **kwargs):
        return await self.request('HEAD', *args, **kwargs)

    async def options(self, *args, **kwargs):
        return await self.request('OPTIONS', *args, **kwargs)


@dataclasses.dataclass
class JsonBaseClient(BaseClient):
    @staticmethod
    async def handle_response(response: aiohttp.ClientResponse) -> dict:
        return await response.json()
