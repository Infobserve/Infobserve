import asyncio

import aiohttp
import asyncpg

from infobserve.common import APP_LOGGER
from infobserve.events import GistEvent

from .base import SourceBase


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

    async def fetch_events(self, pool=None):
        """Fetches the most recent gists created.

        Arguments:
            pool (asyncpg.Pool): A db connection pool lease connections.

        Returns:
            event_list (list) : A list of GistEvent Objects.
        """

        headers = {
            "user-agent": 'Infobserver',
            "Accept": self._api_version,
            "Authorization": f'token {self._oauth_token}'
        }

        async with aiohttp.ClientSession() as session:
            resp = await session.get(self._uri, headers=headers)
            gists = await resp.json()
            APP_LOGGER.debug("GistSource: %s Fetched Recent 30 Gists", self.name)

            cached_ids = await self._query_index_cache(pool)
            event_list = list()
            tasks = list()
            gists = list(filter(lambda elem: elem["id"] not in cached_ids, gists))
            APP_LOGGER.debug("Gists number not in cache: %s", len(gists))

            for gist in gists:
                # Create GistEvent objects and create io intensive tasks.
                ge = GistEvent(gist)
                event_list.append(ge)
                tasks.append(asyncio.create_task(ge.fetch(session)))

            await self._update_index_cache(pool, [x["id"] for x in gists])

            await asyncio.gather(*tasks)  # Fetch the raw content async
            APP_LOGGER.debug("%s GistEvents send for processing", len(gists))
            return event_list

    async def fetch_events_scheduled(self, queue, pool=None):
        """Call the fetch_events method on a schedule.

        Arguments:
           queue (Queue): A queue to enqueue the events.
           pool (asyncpg.Pool): A db connection pool lease connections.
        """
        while True:
            events = await self.fetch_events(pool)
            for event in events:
                await queue.queue_event(event)

            await asyncio.sleep(self.timeout)

    async def _query_index_cache(self, pool):
        """Query the cache for indexed gists.

        Arguments:
            pool (asyncpg.Pool): A connection pool to lease a db connection.

        Returns:
            (list): Returns a list with the cached ids for the source.
        """

        async with pool.acquire() as conn:
            stmt = await conn.prepare("""SELECT SOURCE_ID FROM INDEX_CACHE WHERE SOURCE = 'gist' """)
            results = await stmt.fetch()
            APP_LOGGER.debug("Fetched INDEX_CACHE with %s cached gists.", len(results))
        return [x["source_id"] for x in results]

    async def _update_index_cache(self, pool, source_ids):
        """Insert the indexed gists ids to cache.

        Arguments:
            pool (asyncpg.Pool): A connection pool to lease a db connection.
        """
        async with pool.acquire() as conn:
            data = list()
            for source_id in source_ids:
                data.append(("gist", source_id))
            await conn.copy_records_to_table('index_cache', records=data, columns=["source", "source_id"])
            APP_LOGGER.debug("Updated INDEX_CACHE for gists")
