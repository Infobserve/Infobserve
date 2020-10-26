""" The IndexCache class implementation """
from infobserve.common import APP_LOGGER
from infobserve.common.pools import PgPool


class IndexCache():
    """Manages the INDEX_CACHE table."""

    def __init__(self, source):
        """Constructor
        Arguments:
            source (str): The source name.
        """

        self.source = source

    async def query_index_cache(self):
        """Query the cache for indexed gists.

        Arguments:
            pool (asyncpg.Pool): A connection pool to lease a db connection.

        Returns:
            (list): Returns a list with the cached ids for the source.
        """

        async with PgPool().acquire() as conn:
            stmt = await conn.prepare(f"""SELECT SOURCE_ID FROM INDEX_CACHE WHERE SOURCE = '{self.source}' """)
            results = await stmt.fetch()

        return [x["source_id"] for x in results]

    async def update_index_cache(self, source_ids):
        """Insert the indexed gists ids to cache.

        Arguments:
            pool (asyncpg.Pool): A connection pool to lease a db connection.
        """
        async with PgPool().acquire() as conn:
            data = list()
            for source_id in source_ids:
                data.append((self.source, source_id))
            await conn.copy_records_to_table('index_cache', records=data, columns=["source", "source_id"])
