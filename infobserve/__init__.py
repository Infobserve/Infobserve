"""The main entrypoint and interface of the infobserver application.
"""
import asyncio
from .config import CONFIG
from .logger import APP_LOGGER
from .processing.queue import EventQueue
from .sources import GistSource

__version__ = '0.1.0'


def init_sources(config):
    sources = list()
    for conf_source in config:
        APP_LOGGER.debug("conf_source:%s", conf_source)
        sources.append(GistSource(conf_source, name="Gist"))
    return sources


async def log_consumer(queue):
    while True:
        event = await queue.get_event()
        APP_LOGGER.debug("Consumed Timestamp:%s File:%s Size:%s Creator:%s ", event.timestamp, event.filename,
                         event.size, event.creator)


def source_scheduler(sources, loop):
    for source in sources:
        APP_LOGGER.debug("Scheduling Source:%s", source.name)
        loop.create_task(source.fetch_events_scheduled(EventQueue.get_instance()))

    return loop


def consumer_scheduler():
    pass


if __name__ == "__main__":
    APP_LOGGER.info("Logging up and running")
    APP_LOGGER.debug("Configured Sources:%s", CONFIG.SOURCES)
    main_loop = asyncio.get_event_loop()
    main_loop = source_scheduler(init_sources(CONFIG.SOURCES), main_loop)
    main_loop.create_task(log_consumer(EventQueue.get_instance()))
    APP_LOGGER.debug("Consumer Scheduled")
    APP_LOGGER.info("Main Loop Initialized")
    main_loop.run_forever()
