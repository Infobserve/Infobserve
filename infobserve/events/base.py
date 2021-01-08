'''Declare the base event class '''
import json
from abc import ABCMeta, abstractmethod
from datetime import datetime

from infobserve.common.logger import APP_LOGGER


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

        self.timestamp = self.timestamp.strftime(r"%Y/%m/%d-%H:%M:%S")
        self.source = source
        self.raw_content = None

    @abstractmethod
    async def realize_raw_content(self, session):
        """Retrieve the raw content of the event.

        You can use it as a getter or implement logic to fetch the raw content.
        In case it is not provided from the source and a secondary request is required.
        """

    def is_valid(self):
        """Checks if the event has enough information to be processed.

        Returns: (bool)
        """
        if not self.raw_url:
            return False

        return True

    def to_json(self):
        """Converts an Event object to a json string

        Returns:
            string: The json string representation of the object
        """

        j = {
            'url': self.raw_url,
            'size': self.size,
            'source': self.source,
            'raw_content': self.raw_content,
            'filename': self.filename,
            'creator': self.creator,
            'created_at': self.timestamp,
            'discovered_at': datetime.now().strftime(r"%Y/%m/%d-%H:%M:%S")
        }

        return json.dumps(j)
