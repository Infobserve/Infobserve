"""The main entrypoint and interface of the infobserver application.
"""
import asyncio

from .common import CONFIG
from .common import APP_LOGGER
from .common.queue import ProcessingQueue
from .sources import SOURCE_FACTORY

__version__ = '0.1.0'


def init_sources(config):
    sources = list()
    for conf_source in config:
        APP_LOGGER.debug("conf_source:%s", conf_source)
        sources.append(SOURCE_FACTORY.get_source(conf_source))
    return sources


async def log_consumer(queue):
    while True:
        event = await queue.get_event()
        APP_LOGGER.debug("Consumed Timestamp:%s File:%s Size:%s Creator:%s ", event.timestamp, event.filename,
                         event.size, event.creator)


def source_scheduler(sources, loop, processing_queue):
    for source in sources:
        APP_LOGGER.debug("Scheduling Source:%s", source.name)
        loop.create_task(source.fetch_events_scheduled(processing_queue))

    return loop


def consumer_scheduler():
    pass


def main():
    APP_LOGGER.info("Logging up and running")
    APP_LOGGER.debug("Configured Sources:%s", CONFIG.SOURCES)
    processing_queue = ProcessingQueue(CONFIG.PROCESSING_QUEUE_SIZE)

    main_loop = asyncio.get_event_loop()

    pg_pool = main_loop.run_until_complete(CONFIG.init_db_pool())

    main_loop = source_scheduler(init_sources(CONFIG.SOURCES), main_loop, processing_queue)
    main_loop.create_task(log_consumer(processing_queue))
    APP_LOGGER.debug("Consumer Scheduled")
    APP_LOGGER.info("Main Loop Initialized")
    main_loop.run_forever()


if __name__ == "__main__":
    main()
