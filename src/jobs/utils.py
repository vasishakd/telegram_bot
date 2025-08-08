import asyncio
import logging
import typing
from functools import wraps

log = logging.getLogger(__name__)


def periodic_task_run(sleep: int):
    """
    :param sleep: Задержка в секундах
    """

    def _periodic_task_run(coro: typing.Callable):
        @wraps(coro)
        async def _wrapper(*args, **kwargs):
            async def _run(*args, **kwargs):
                try:
                    await coro(*args, **kwargs)
                except Exception as e:
                    log.error('Get exception when process task %s', e, exc_info=True)

            log.debug('Running job "%s"', coro.__name__)
            if not sleep:
                await _run(*args, **kwargs)
                return

            while True:
                await _run(*args, **kwargs)
                await asyncio.sleep(sleep)

        return _wrapper

    return _periodic_task_run
