'''Declare the base event class '''
from abc import ABCMeta, abstractmethod
from datetime import datetime
from infobserve.common import APP_LOGGER


class BaseEvent(metaclass=ABCMeta):
    """The Abstract Base Class of Events.

    This class represents a basis to represent the events
    created from data sources.

    Attributes:
        timestamp (datetime): The creation timestamp.
        source (string): The source the event comes from.
    """

    def __init__(self, timestamp, source=None):
        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

        self.source = source

    @abstractmethod
    async def get_raw_content(self, session):
        """Retrieve the raw content of the event.

        You can use it as a getter or implement logic to fetch the raw content.
        In case it is not provided from the source and a secondary request is required.
        """
