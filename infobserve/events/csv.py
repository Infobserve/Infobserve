import base64

from .base import BaseEvent
import binascii


class CsvEvent(BaseEvent):
    """The Events created from recent gists.

    Attributes:
        id (string): A unique id that  github uses for gists.
        raw_url (string): The url that points to the raw content.
        size (int): The size in bytes.
        filename (string): The name of the file.
        creator (string): The name of the creator.
        raw_content (string): The content.
    """

    def __init__(self, csv):
        """Instantiates the GistEvent.

        Arguments:
            paste (Paste): Paste object by pbwrap package.
        """
        BaseEvent.__init__(self, csv[2], source="csv")
        self.id = csv[0]
        self.filename = csv[4]
        self.creator = csv[3]
        self.raw_content = None
        self.raw_content = csv[5]

    async def get_raw_content(self):
        """Retrieves the raw content of the gist.

        Arguments:
            session (aio.http.session): An aio http session to avoid opening and closing connections.

        Returns:
            raw_content (string): The content of the gist.
        """
        try:
            return str(base64.b64decode(self.raw_content)).encode(encoding='utf-8')
        except binascii.Error:
            print("GOT FUCKED BY BINASCII")
