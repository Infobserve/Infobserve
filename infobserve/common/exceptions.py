"""
This modules contains all of infobserve's exceptions
"""


class BadCredentials(Exception):
    pass


class UnitializedRedisConnectionPool(Exception):
    pass
