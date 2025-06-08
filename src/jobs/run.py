import asyncio
import logging

import uvloop

from src.db import utils as db_utils
from src.jobs import tasks

log = logging.getLogger(__name__)

Session = db_utils.init_db()


# noinspection PyAsyncCall
async def main():
    asyncio.create_task(tasks.check_notifications_anime())
    asyncio.create_task(tasks.check_notifications_manga())


if __name__ == '__main__':
    uvloop.install()

    log.info('Init db')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
