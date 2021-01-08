import asyncio
from json.decoder import JSONDecodeError
from typing import List

import aiohttp
from pbwrap import AsyncPastebin, Paste  # type: ignore

from infobserve.common import APP_LOGGER
from infobserve.common.queue import RedisQueue
from infobserve.events import PasteEvent

from .base import SourceBase


class PastebinSource(SourceBase):
    """The implementation of Pastebin Source.
    """

    def __init__(self, config, name: str = None):
        SourceBase.__init__(self, name=name)
        self.SOURCE_TYPE: str = "pastebin"
        self.pastebin: AsyncPastebin = AsyncPastebin(dev_key=config.get("dev_key"))
        self.timeout: float = float(config.get("timeout"))

    async def fetch_events(self):
        pastes: List[Paste] = self.pastebin.get_recent_pastes(limit=50)
        event_list = []
        tasks = []

        for paste in pastes:
            paste_event = PasteEvent(paste)

            if paste_event.is_valid():
                event_list.append(paste_event)
                tasks.append(asyncio.create_task(paste_event.get_raw_content()))
            else:
                APP_LOGGER.warning("Dropped event with id:%s url not valid", paste_event.id)

        await asyncio.gather(*tasks)  # Fetch the raw content async
        event_list = [x for x in event_list if x.raw_content]

        APP_LOGGER.debug("%s PastebinEvents send for processing", len(event_list))
        return event_list

    async def fetch_events_scheduled(self, queue: RedisQueue):
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
