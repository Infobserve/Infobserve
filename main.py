"""The main entrypoint and interface of the infobserver application.
"""
import asyncio

from infobserve.common import APP_LOGGER, CONFIG
from infobserve.common.pools import RedisConnectionPool, PgPool
from infobserve.common.queue import ProcessingQueue
from infobserve.loaders.postgres import PgLoader
from infobserve.processors.yara_processor import YaraProcessor
from infobserve.schedulers.source import SourceScheduler

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

    pg_pool = PgPool()
    main_loop.run_until_complete(pg_pool.init_db())

    if CONFIG.REDIS_CONFIG:
        redis_pool = RedisConnectionPool()
        main_loop.run_until_complete(redis_pool.init_redis_pool())
    else:
        APP_LOGGER.warning("No Redis Connection Configured falling back to simple Asyncio Queues")

    source_queue = ProcessingQueue("raw_events", CONFIG.PROCESSING_QUEUE_SIZE)
    # TODO: Add DB queue size option in the config?
    db_queue = ProcessingQueue("processed_events")
    sources_scheduler = SourceScheduler(source_queue, sources=CONFIG.SOURCES)

    main_loop = sources_scheduler.schedule(main_loop)
    main_loop = consumer_scheduler(main_loop, source_queue, db_queue)

    APP_LOGGER.debug("Consumer Scheduled")
    APP_LOGGER.info("Main Loop Initialized")
    main_loop.run_forever()


if __name__ == "__main__":
    main()
