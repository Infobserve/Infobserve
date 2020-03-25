"""This module contains the source
"""
from abc import ABCMeta, abstractmethod


class SourceBase(metaclass=ABCMeta):
    """An abstract class to describe a base Source.
    """

    def __init__(self, name=None):
        self.name = name

    @abstractmethod
    async def fetch_events(self):
        pass
