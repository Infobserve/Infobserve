'''Declare the base event class '''
from abc import ABCMeta, abstractmethod


class BaseEvent(metaclass=ABCMeta):
    """The Abstract Base Class of Events.

    This class represents a basis to represent the events
    created from data sources.

    Attributes:
        timestamp (string): The creation timestamp as a source.
        source (string): The source the event comes from.
    """

    def __init__(self, timestamp, source=None):
        self.timestamp = timestamp
        self.source = source

    @abstractmethod
    async def get_raw_content(self):
        """Retrieve the raw content of the event.

        You can use it as a getter or implement logic to fetch the raw content.
        In case it is not provided from the source and a secondary request is required.
        """
