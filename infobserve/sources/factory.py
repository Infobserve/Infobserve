"""The Source Entity SourceFactory use this to instantiate Source Entities"""
from .gist import GistSource
from .pastebin import PastebinSource
from .github import GithubSource
from .csv import CsvSource


class SourceFactory():
    """The SourceFactory Class returns the appropriate Source Object."""

    def __init__(self):
        """Initializes the SourceFactory Object."""
        self._sources = dict()
        self.register_source("gist", GistSource)
        self.register_source("pastebin", PastebinSource)
        self.register_source("github-public-events", GithubSource)
        self.register_source("csv", CsvSource)

    def register_source(self, source_type, constructor):
        """Registers a Source Class into the SourceFactory.

        Arguments:
            source_type (str): The type of the source.
            constructor (cls): A source class.
        """
        self._sources[source_type] = constructor

    def get_source(self, config):
        """Returns a Source Object depending on the type.

        Arguments:
            config (dict): A dictionary with the configs to instantiate a Source.

        Returns:
            source (BaseSource): A Source Object.
        """
        source = self._sources.get(config.get("type"))
        if not source:
            raise ValueError(config.get("type"))
        return source(config, name=config.get("type"))
