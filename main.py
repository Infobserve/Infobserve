"""The main entrypoint and interface of the infobserver application.
"""
import asyncio

from infobserve.common.queue import RedisQueue
from infobserve.common import APP_LOGGER, CONFIG
from infobserve.common.pools import RedisConnectionPool
from infobserve.schedulers.source import SourceScheduler

__version__ = '0.1.0'

def main():
    # Initialize Yara Processing queue
    main_loop = asyncio.get_event_loop()

    redis_pool = RedisConnectionPool()
    main_loop.run_until_complete(redis_pool.init_redis_pool())

    source_queue = RedisQueue("events")
    sources_scheduler = SourceScheduler(source_queue, sources=CONFIG.SOURCES)

    main_loop = sources_scheduler.schedule(main_loop)

    APP_LOGGER.debug("Consumer Scheduled")
    APP_LOGGER.info("Main Loop Initialized")
    main_loop.run_forever()


if __name__ == "__main__":
    main()
