import asyncio
from json.decoder import JSONDecodeError
from typing import Dict, List

import aiohttp
from pbwrap import AsyncPastebin, Paste

from infobserve.common import APP_LOGGER
from infobserve.common.index_cache import IndexCache
from infobserve.common.queue import ProcessingQueue
from infobserve.events.event import PasteEvent

from .base import SourceBase


class PastebinSource(SourceBase):
    """The implementation of Pastebin Source.
    """

    def __init__(self, config, name: str = None):
        if name:
            self.name = name

        self.SOURCE_TYPE: str = "pastebin"
        self.pastebin: AsyncPastebin = AsyncPastebin(dev_key=config.get("dev_key"))
        self.timeout: float = float(config.get("timeout"))
        self._index_cache: IndexCache = IndexCache(self.SOURCE_TYPE)

    async def fetch_events(self):
        pastes: List[Paste] = self.pastebin.get_recent_pastes(limit=50)

        if self._index_cache:
            cached_ids = await self._index_cache.query_index_cache()
            pastes = list(filter(lambda elem: elem.key not in cached_ids, pastes))
            APP_LOGGER.debug("Pastes number not in cache: %s", len(pastes))

        event_list = list()
        tasks = list()
        for paste in pastes:
            paste_event = PasteEvent(paste)

            if paste_event.is_valid():
                event_list.append(paste_event)
                tasks.append(asyncio.create_task(paste_event.get_raw_content()))
            else:
                APP_LOGGER.warning("Dropped event with id:%s url not valid", paste_event.id)

            if self._index_cache:
                await self._index_cache.update_index_cache([x.key for x in pastes])

        await asyncio.gather(*tasks)  # Fetch the raw content async

        APP_LOGGER.debug("%s PastebinEvents send for processing", len(event_list))
        return event_list

    async def fetch_events_scheduled(self, queue: ProcessingQueue):
        """
        Call the fetch_events method on a schedule.

        Arguments:
           queue (ProcessingQueue): A processing queue to enqueue the events.
        """
        while True:
            try:
                events = await self.fetch_events()
                for event in events:
                    await queue.queue_event(event)
            except aiohttp.client_exceptions.ClientPayloadError:
                APP_LOGGER.warning("There was an error retrieving the payload will retry in next cycle.")
            except JSONDecodeError:
                APP_LOGGER.warning("IP is not whitelisted in Pastebin!")

            await asyncio.sleep(self.timeout)
