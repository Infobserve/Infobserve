"""The main entrypoint and interface of the infobserver application.
"""
import asyncio

from infobserve.common import APP_LOGGER, CONFIG
from infobserve.common.queue import ProcessingQueue
from infobserve.loaders.postgres import PgLoader
from infobserve.processors.yara_processor import YaraProcessor
from infobserve.schedulers.source import SourceScheduler
from infobserve.sources.csv import CsvSource

__version__ = '0.1.0'


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
    # Initialize Yara Processing queue
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(CONFIG.init_db())
    main_loop.run_until_complete(CONFIG.init_redis_pool())
    APP_LOGGER.info("Initialized Schema")

    APP_LOGGER.info("Logging up and running")
    source_queue = ProcessingQueue("raw_events", CONFIG.PROCESSING_QUEUE_SIZE)
    # TODO: Add DB queue size option in the config?
    db_queue = ProcessingQueue("processed_events")
    sources_scheduler = SourceScheduler(source_queue, sources=CONFIG.SOURCES)

    main_loop = sources_scheduler.schedule(main_loop)
    main_loop = consumer_scheduler(main_loop, source_queue, db_queue)

    APP_LOGGER.debug("Consumer Scheduled")
    APP_LOGGER.info("Main Loop Initialized")
    main_loop.run_forever()


def main2():

    source_queue = ProcessingQueue("raw_events", CONFIG.PROCESSING_QUEUE_SIZE)
    db_queue = ProcessingQueue("processed_events")
    producer = CsvSource(CONFIG.SOURCES[0]["path"])
    consumer = YaraProcessor(CONFIG.YARA_RULES_PATHS, source_queue, db_queue)

    asyncio.run(producer.fetch_events_scheduled(source_queue))
    asyncio.run(consumer.process2())


if __name__ == "__main__":
    main2()
