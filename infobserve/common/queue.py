import pickle

from aioredis import Redis

from .pools import RedisConnectionPool


class RedisQueue:
    def __init__(self, name, max_queue_size=0):
        self.name = name

        redis_pool = RedisConnectionPool()
        self.__queue = redis_pool

    async def queue_event(self, event, block=True):
        """
        Inserts a new event into the processing queue

        Args:
            event (RawEvent): The event to insert into the queue
            block (bool): Determines whether the process can block during
                            the insertion of a new event in case the
                            processing queue is full
                            (determined during instantiation).
                            In such case, an exception is raised
        Raises:
            asyncio.QueueFull: If `block` is False and the queue is
                                full
        """
        with await self.__queue.redis as conn:
            redis = Redis(conn)
            await redis.lpush(self.name, event)

    def notify(self):
        """
        Notifies processes that a task that has been inserted into the
        processing queue has been completed, using `asyncio.task_done`.
        Each call to `get_event` should be followed by a call to `notify`.

        Raises:
            ValueError: If called more times than than there were items
                        placed in the processing queue
        """
        if self.type == self.REDIS_QUEUE:
            pass
        else:
            self.__queue.task_done()

    async def events_left(self):
        """
        Returns:
            The Event objects that have not yet been processed by the queue.
        """
        with await self.__queue.redis as conn:
            redis = Redis(conn)
            return await redis.llen(self.name)
