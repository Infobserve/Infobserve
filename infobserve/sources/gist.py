import asyncio
from typing import Any, Dict, List, Optional, Union

import aiohttp

from infobserve.common import APP_LOGGER
from infobserve.common.exceptions import BadCredentials
from infobserve.common.queue import RedisQueue
from infobserve.events import GistEvent

from .base import SourceBase

BAD_CREDENTIALS = "Bad credentials"


class GistSource(SourceBase):
    """The implementation of Gist Source.

    This Class represents the github gist as a source of data it fetches
    the latest number of gists specified in config and creates list of those
    gists represented as GistEvent objects.

    Attributes:
        SOURCE_TYPE (string): The type of the source.
        _oauth_token (string): The oauth token for the github api.
        _username (string): The username of the user to authenticate.
        _uri (string): Gitlab's api uri.
        _api_version (string): Gitlab's api version.
        _timeout(float): The frequency the gists endpoint is queried
    """

    def __init__(self, config: Dict, name: str = None):
        SourceBase.__init__(self, name=name)
        self.SOURCE_TYPE: str = "gist"
        self._oauth_token: Optional[Any] = config.get('oauth')
        self._username: Optional[Any] = config.get('username')
        self._uri: str = "https://api.github.com/gists/public?"
        self._api_version: str = "application/vnd.github.v3+json"
        self.timeout: Union[float] = config.get('timeout', 60)

    async def fetch_events(self) -> List[GistEvent]:
        """
        Fetches the most recent gists created.

        Returns:
            event_list (list) : A list of GistEvent Objects.
        """

        headers: Dict = {
            "user-agent": 'Infobserver',
            "Accept": self._api_version,
            "Authorization": f'token {self._oauth_token}'
        }

        async with aiohttp.ClientSession() as session:
            resp = await session.get(self._uri, headers=headers)
            gists = await resp.json()
            event_list = []
            tasks = []

            if isinstance(gists, dict) and gists["message"] == BAD_CREDENTIALS:
                raise BadCredentials("Could not authenticate against github API with the provided credentials")

            APP_LOGGER.debug("GistSource: %s Fetched Recent %s Gists", self.name, len(gists))
            APP_LOGGER.debug("Gists number not in cache: %s", len(gists))

            for gist in gists:
                # Create GistEvent objects and create io intensive tasks.
                ge = GistEvent(gist)

                if ge.is_valid():
                    event_list.append(ge)
                    tasks.append(asyncio.create_task(ge.realize_raw_content(session)))
                else:
                    APP_LOGGER.warning("Dropped event with id:%s url not valid", ge.id)

            # Fetch the raw content async.
            await asyncio.gather(*tasks)
            # filter out event with no raw_content.
            event_list = [x for x in event_list if x.raw_content]
            APP_LOGGER.debug("%s GistEvents send for processing", len(gists))
            return event_list

    async def fetch_events_scheduled(self, queue: RedisQueue):
        """
        Call the fetch_events method on a schedule.

        Arguments:
           queue (ProcessingQueue): A processing queue to enqueue the events.
        """
        while True:
            try:
                events: List[GistEvent] = await self.fetch_events()
                for event in events:
                    await queue.queue_event(event.to_json())
            except aiohttp.client_exceptions.ClientPayloadError:
                APP_LOGGER.warning("There was an error retrieving the payload will retry in next cycle.")

            await asyncio.sleep(self.timeout)
