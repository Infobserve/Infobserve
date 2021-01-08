""" Singleton Connection Pools for Postgresql and Redis """

import sys

import aioredis

from . import APP_LOGGER, CONFIG


class Singleton(type):
    _instances = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisConnectionPool(metaclass=Singleton):
    redis = None

    async def init_redis_pool(self):
        """Initialize Redis connection pool.
        """
        try:
            self.redis: aioredis.RedisPool = await aioredis.create_pool(
                (CONFIG.REDIS_CONFIG["host"], CONFIG.REDIS_CONFIG["port"]))
        except KeyError:
            APP_LOGGER.error("Wrong configuration format for redis key in yaml")
            sys.exit(1)
