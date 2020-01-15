'''Declare the base event class '''


class Event():

    def __init__(self, source, timestamp, url):
        self.source = source
        self.timestamp = timestamp
        self.url = url

    def process_event(self):
        pass


class GistEvent(Event):

    def __init__(self, source, timestamp, url):
        super().__init__(source, timestamp, url)
        self.raw_content = "WIP"
        self.size = "WIP"  # Bytes
        self.filename = "WIP"
        self.creator = "WIP"
