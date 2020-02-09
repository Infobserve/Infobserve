""" Singleton Connection Pool for Postgresql """
import asyncpg


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PgPool(metaclass=Singleton):

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
