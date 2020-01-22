import asyncio

import aiohttp

from infobserve.logger import APP_LOGGER
from infobserve.models import GistEvent

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
        SourceBase.__init__(name)

        self.SOURCE_TYPE = "gist"
        self._oauth_token = config.get('oauth')
        self._username = config.get('username')
        self._uri = "https://api.github.com/gists/public?"
        self._api_version = "application/vnd.github.v3+json"

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
            APP_LOGGER.debug("GistSource fetched gists")

            event_list = list()
            tasks = list()
            for gist in gists:
                ge = GistEvent(gist)
                event_list.append(ge)
                tasks.append(asyncio.create_task(ge.fetch(session)))

            await asyncio.gather(*tasks)  # Fetch the raw content async
            APP_LOGGER.debug("%s GistEvents send for processing", len(gists))
            return event_list
