from datetime import datetime

from .base import BaseEvent


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
        self.raw_url = paste.scrape_url
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
            return None
        return self.raw_content
