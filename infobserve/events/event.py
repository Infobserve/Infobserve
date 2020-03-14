"""The implementation of the GistEvent Class."""
import asyncio

from .base import BaseEvent
from datetime import datetime


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
        """Instantiates the GistEvent.

        Arguments:
            raw_gist (dict): A complex dictionary returned by the gist API.
        """
        BaseEvent.__init__(self, raw_gist.get("created_at"), source="gist")

        unpacked_files_key = self._unpack(raw_gist.get("files"))
        self.id = raw_gist.get("id")
        self.raw_url = unpacked_files_key.get("raw_url")
        self.size = unpacked_files_key.get("size")
        self.filename = unpacked_files_key.get("filename")
        self.creator = raw_gist["owner"].get("login")
        self.raw_content = None

    async def get_raw_content(self, session):
        """Retrieves the raw content of the gist.

        Arguments:
            session (aio.http.session): An aio http session to avoid opening and closing connections.

        Returns:
            raw_content (string): The content of the gist.
        """
        try:
            async with await session.get(self.raw_url) as response:
                try:
                    self.raw_content = await response.text()
                except UnicodeDecodeError:
                    return None
            return self.raw_content
        except asyncio.TimeoutError:
            return None

    @staticmethod
    def _unpack(nested_dict):
        """Helps unpack the "files" key returned from the gist api.

        At the moment supports only 1 key->dictionary from the "files" key.
        If the "files" key contains not valid values it will return an empty dict()
        Arguments:
            nested_dict (dict): The "files" key dictionary from a gist.
        Returns:
            (dict): The unpacked nested dictionary
        """
        for value in nested_dict.values():
            if value:
                return value
        return dict()

    def is_valid(self):
        """Checks if the event has enough information to be processed.

        Returns: (bool)
        """
        if not self.raw_url:
            return False

        return True


class PasteEvent(BaseEvent):
    """The Events created from recent gists.

    Attributes:
        id (string): A unique id that  github uses for gists.
        raw_url (string): The url that points to the raw content.
        size (int): The size in bytes.
        filename (string): The name of the file.
        creator (string): The name of the creator.
        raw_content (string): The content.
    """

    def __init__(self, paste):
        """Instantiates the GistEvent.

        Arguments:
            paste (Paste): Paste object by pbwrap package.
        """
        BaseEvent.__init__(self, datetime.fromtimestamp(int(paste.date)), source="pastebin")

        self.id = paste.key
        self.raw_url = "https://pastebin.com/raw/" + self.id
        self.size = paste.size
        self.filename = paste.title
        self.creator = "Anonymous"
        self.raw_content = None
        self.paste = paste

    async def get_raw_content(self):
        """Retrieves the raw content of the gist.

        Arguments:
            session (aio.http.session): An aio http session to avoid opening and closing connections.

        Returns:
            raw_content (string): The content of the gist.
        """
        try:
            self.raw_content = self.paste.scrape_raw_text()
        except UnicodeDecodeError:
            return self.raw_content
        return self.raw_content

    def is_valid(self):
        """Checks if the event has enough information to be processed.

        Returns: (bool)
        """
        if not self.raw_url:
            return False

        return True