'''Declare the base event class '''
from abc import ABCMeta, abstractmethod


class BaseEvent(metaclass=ABCMeta):
    """The Abstract Base Class of Events.

    This class represents a basis to represent the events
    created from data sources.

    Attributes:
        timestamp (string): The creation timestamp as a source.
        source (string): The source the event comes from
    """

    def __init__(self, timestamp, source=None):
        self.timestamp = timestamp
        self.source = source

    @abstractmethod
    def process_event(self):
        pass


class GistEvent(BaseEvent):
    """The Events created from recent gists.

    Attributes:
        id (string): A unique id that  github uses for gists.
        raw_url (string): The url that points to the raw content.
        size (int): The size in bytes.
        filename (string): The name of the file.
        creator (string): The name of the creator.
        raw_content (string): The content.
    """

    def __init__(self, raw_gist):
        BaseEvent.__init__(self, raw_gist.get("created_at"), source="gist")

        unpacked_files_key = self.unpack(raw_gist.get("files"))
        self.id = raw_gist["id"]
        self.raw_url = unpacked_files_key["raw_url"]
        self.size = unpacked_files_key["size"]
        self.filename = unpacked_files_key["filename"]
        self.creator = raw_gist["owner"]["login"]
        self.raw_content = None

    async def fetch(self, session):
        """Retrieves the raw content of the gist.

        Arguments:
            session (aio.http.session): An aio http session to avoid opening and closing connections.

        Returns:
            raw_content (string): The content of the gist.
        """
        async with session.get(self.raw_url) as response:
            resp = await session.get(self.raw_url)
            self.raw_content = await resp.text()
        return self.raw_content

    @staticmethod
    def unpack(nested_dict):
        """
        Helps unpack the files key returned from the gist api.
        """
        for value in nested_dict.values():
            return value

    def process_event(self):
        pass
