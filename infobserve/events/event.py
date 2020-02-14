"""The implementation of the GistEvent Class."""
from .base import BaseEvent


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
        async with session.get(self.raw_url) as response:
            resp = await session.get(self.raw_url)
            self.raw_content = await resp.text()
        return self.raw_content

    @staticmethod
    def _unpack(nested_dict):
        """
        Helps unpack the files key returned from the gist api.
        """
        for value in nested_dict.values():
            return value

    def is_valid(self):
        """Checks if the event has enough information to be processed.

        Returns: (bool)
        """
        if not self.raw_url:
            return False

        return True
