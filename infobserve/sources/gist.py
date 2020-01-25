import asyncio

import aiohttp

from infobserve.common import APP_LOGGER
from infobserve.events import GistEvent

from .source import SourceBase


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
    """

    def __init__(self, config, name=None):
        if name:
            self.name = name

        self.SOURCE_TYPE = "gist"
        self._oauth_token = config.get('oauth')
        self._username = config.get('username')
        self._uri = "https://api.github.com/gists/public?"
        self._api_version = "application/vnd.github.v3+json"
        self.timeout = config.get('timeout')

    async def fetch_events(self):
        """Fetches the most recent gists created."""

        headers = {
            "user-agent": 'Infobserver',
            "Accept": self._api_version,
            "Authorization": f'token {self._oauth_token}'
        }

        async with aiohttp.ClientSession() as session:
            resp = await session.get(self._uri, headers=headers)
            gists = await resp.json()
            APP_LOGGER.debug("GistSource: %s Fetched Recent 30 Gists", self.name)
            event_list = list()
            tasks = list()
            for gist in gists:

                ge = GistEvent(gist)
                event_list.append(ge)
                tasks.append(asyncio.create_task(ge.fetch(session)))

            await asyncio.gather(*tasks)  # Fetch the raw content async
            APP_LOGGER.debug("%s GistEvents send for processing", len(gists))
            return event_list

    async def fetch_events_scheduled(self, queue):
        while True:
            events = await self.fetch_events()
            for event in events:
                await queue.queue_event(event)

            await asyncio.sleep(self.timeout)
