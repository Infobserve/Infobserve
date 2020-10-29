""" Singleton Connection Pools for Postgresql and Redis """

import sys

import aioredis
import asyncpg

from . import APP_LOGGER, CONFIG


class Singleton(type):
    _instances = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PgPool(metaclass=Singleton):

    async def init_db_pool(self):
        """Initialize the database connection pool
        """
        self.pool = await asyncpg.create_pool(**CONFIG.DB_CONFIG)

    def acquire(self):
        """ Encapsulate the acquire() method of the asyncpg.Pool object.

        Returns:
            (asyncpg.connection.Connection): A Connection instance.
        """
        return self.pool.acquire()

    async def init_db(self):
        """Initialize the database.
        """
        await self.init_db_pool()

        async with self.acquire() as conn:
            with open("infobserve-schema.sql") as init_script:
                try:
                    async with conn.transaction() as tr:
                        await conn.execute(init_script.read())
                        APP_LOGGER.info("Initialized Schema")
                # The init script should move to schema level and so does this error.
                # To be refactored soon it's stupid to log this we should initialize the database
                # And run the migrations normally.
                except asyncpg.exceptions.DuplicateTableError:
                    APP_LOGGER.warning("Duplicate Table Error Raised the sql init script failed.")


class RedisConnectionPool(metaclass=Singleton):

    async def init_redis_pool(self):
        """Initialize Redis connection pool.
        """
        try:
            self.redis: aioredis.RedisPool = await aioredis.create_pool(
                (CONFIG.REDIS_CONFIG["host"], CONFIG.REDIS_CONFIG["port"]))
        except KeyError:
            APP_LOGGER.error("Wrong configuration format for redis key in yaml")
            sys.exit(1)
