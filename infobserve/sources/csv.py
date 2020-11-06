import asyncio
import csv
from typing import Any, Dict, List, Optional, Union

import io
from infobserve.common import APP_LOGGER
from infobserve.common.index_cache import IndexCache
from infobserve.common.queue import ProcessingQueue
from infobserve.events.csv import CsvEvent

from .base import SourceBase


class CsvSource(SourceBase):

    def __init__(self, path: str, name: str = None):
        SourceBase.__init__(self, name=name)
        self.SOURCE_TYPE: str = "csv-source"
        self._path: str = path

    async def fetch_events(self):
        csv.field_size_limit(100000000)
        with open(self._path) as csv_read:
            event_list: List[CsvEvent] = []
            task_list = []
            data = csv_read.read()
            reader = csv.reader(io.StringIO(data))
            for row in reader:
                try:
                    event_list.append(CsvEvent(row))
                    task_list.append(asyncio.create_task(event_list[-1].get_raw_content()))
                except KeyError:
                    APP_LOGGER.error("KeyError!")
            asyncio.gather(*task_list)
            event_list.append(None)
            return event_list

    async def fetch_events_scheduled(self, queue: ProcessingQueue):
        """
        Call the fetch_events method on a schedule.

        Arguments:
           queue (ProcessingQueue): A processing queue to enqueue the events.
        """
        events: List[CsvEvent] = await self.fetch_events()
        for event in events:
            await queue.queue_event(event)
        APP_LOGGER.info("Enqueued ALL")