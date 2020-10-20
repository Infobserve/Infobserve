""" Singleton Connection Pool for Postgresql """

import asyncpg
import aioredis
from .exceptions import UnitializedRedisConnectionPool


class Singleton(type):
    _instances = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PgPool(metaclass=Singleton):
    pool = None

    async def init_db_pool(self, db):
        """Initialize the database connection pool.
        Arguments:
            db (dict): A dict with kwargs to initialize the connection pool.
        """
        self.pool = await asyncpg.create_pool(**db)

    def acquire(self):
        """ Encapsulate the acquire() method of the asyncpg.Pool object.

        Returns:
            (asyncpg.connection.Connection): A Connection instance.
        """
        return self.pool.acquire()


class RedisConnectionPool(metaclass=Singleton):
    redis = None

    async def init_redis_pool(self, redis):
        """Initialize Redis connection pool.
        Arguments:
            redis (dict): A dict with kwargs to initialize the connection pool.
        """
        self.redis: aioredis.RedisPool = await aioredis.create_pool((redis["host"], redis["port"]))

    async def acquire(self):
        """
        Returns:
            (aioredis.)
        """
        if self.redis:
            return self.redis

        raise UnitializedRedisConnectionPool()
