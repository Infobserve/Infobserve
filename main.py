"""The main entrypoint and interface of the infobserver application.
"""
import asyncio

from infobserve.common import APP_LOGGER, CONFIG
from infobserve.common.queue import ProcessingQueue
from infobserve.processors.yara_processor import YaraProcessor
from infobserve.sources import SOURCE_FACTORY
from infobserve.loaders.postgres import PgLoader

__version__ = '0.1.0'


def init_sources(config):
    sources = list()
    for conf_source in config:
        APP_LOGGER.debug("conf_source:%s", conf_source)
        sources.append(SOURCE_FACTORY.get_source(conf_source))
    return sources


def source_scheduler(sources, loop, source_queue):
    for source in sources:
        APP_LOGGER.debug("Scheduling Source:%s", source.name)
        loop.create_task(source.fetch_events_scheduled(source_queue))

    return loop


def consumer_scheduler(loop, source_queue, db_queue):
    """
    Creates a YaraProcessor, passing it the Yara rule file paths as read from the config file.

    Args:
        loop (asyncio loop): The loop to add the consumer as a task to
        source_queue (infobserve.common.queue.ProcessingQueue): The queue from which the processor will retrieve
                                                                sources
        db_queue (infobserve.common.queue.ProcessingQueue): The queue into which the processor will place any
                                                            matches
    """
    APP_LOGGER.debug("Starting Yara Processor")
    consumer = YaraProcessor(CONFIG.YARA_RULES_PATHS, source_queue, db_queue)
    db_consumer = PgLoader(db_queue)
    loop.create_task(consumer.process())
    loop.create_task(db_consumer.process())

    return loop


def main():

    APP_LOGGER.info("Logging up and running")
    APP_LOGGER.debug("Configured Sources:%s", CONFIG.SOURCES)
    source_queue = ProcessingQueue(CONFIG.PROCESSING_QUEUE_SIZE)
    # TODO: Add DB queue size option in the config?
    db_queue = ProcessingQueue()

    # Initialize Yara Processing queue

    main_loop = asyncio.get_event_loop()

    main_loop.run_until_complete(CONFIG.init_db())
    APP_LOGGER.info("Initialized Schema")

    main_loop = source_scheduler(init_sources(CONFIG.SOURCES), main_loop, source_queue)
    main_loop = consumer_scheduler(main_loop, source_queue, db_queue)

    APP_LOGGER.debug("Consumer Scheduled")
    APP_LOGGER.info("Main Loop Initialized")
    main_loop.run_forever()


if __name__ == "__main__":
    main()
