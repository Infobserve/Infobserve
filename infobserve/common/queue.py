import asyncio


class ProcessingQueue:

    def __init__(self, max_queue_size=0):
        self.__queue = asyncio.Queue(max_queue_size)

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

        put_method = self.__queue.put if block else self.__queue.put_nowait
        await put_method(event)

    async def get_event(self, block=True):
        """
        Returns the next event to be processed from the queue

        Args:
            block (bool): Determines whether the process can block during
                            the retrieval of the next event to be processed
                            if the processing queue if empty.
                            In such case, an exception is raised
        Returns:
            The next Event object to be processed
        Raises:
            asyncio.QueueEmpty: If `block` is False and the queue is empty

        """

        get_method = self.__queue.get if block else self.__queue.get_nowait
        return await get_method()

    def notify(self):
        """
        Notifies processes that a task that has been inserted into the
        processing queue has been completed, using `asyncio.task_done`.
        Each call to `get_event` should be followed by a call to `notify`.

        Raises:
            ValueError: If called more times than than there were items
                        placed in the processing queue
        """

        self.__queue.task_done()

    async def wait_all(self):
        """
        Blocks execution until all inserted Events have been processed.
        An Event is considered to be processed *after* a call to `notify`
        has been called.
        """

        await self.__queue.join()

    def events_left(self):
        """
        Returns:
            The Event objects that have not yet been processed by the queue.
        """

        return self.__queue.qsize()

    def max_size(self):
        """
        Returns:
            The max size of the queue (as defined in the constructor)
        """
        return self.__queue.maxsize
