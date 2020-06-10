"""The implementation of the GistEvent Class."""
import asyncio
from os import path

from infobserve.common import APP_LOGGER

from .base import BaseEvent


class GithubEvent(BaseEvent):
    """The Events created from Github.

    Attributes:
        id (string): A unique id that  github uses for gists.
        raw_url (string): The url that points to the raw content.
        size (int): The size in bytes.
        filename (string): The name of the file.
        creator (string): The name of the creator.
        raw_content (string): The content.
    """

    def __init__(self, github_event, session):
        """Instantiates the GithubEvent.

        Arguments:
            raw_gist (dict): A complex dictionary returned by the gist API.
        """
        BaseEvent.__init__(self, github_event.get("created_at"), source="github-public-events")

        self.id = github_event.get("id")
        self.creator = github_event["actor"].get("login")
        self.commits = [Commit(x, session) for x in github_event["payload"]["commits"]]
        self.session = session
        self.raw_content = None
        self.filename = None

    async def get_raw_content(self):
        """Retrieves the raw content of all the commits in GithubEvent.
        """
        for commit in self.commits:
            await commit.get_commit_raw_urls()
            await commit.get_raw_content()

    def commit_raw_content(self):
        for commit in self.commits:
            for raw_data in commit.files_raw_data:
                self.raw_content = raw_data[0]
                self.filename = raw_data[1]
                yield self

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


class Commit():
    """The Commit Class represents a commit object from github"""

    def __init__(self, commit_dict, session):
        self.sha = commit_dict.get("sha")
        self.session = session
        self.commit_url = commit_dict.get("url")
        self.files_raw_url = []
        self.files_raw_data = []

    async def get_commit_raw_urls(self):
        try:
            async with self.session.get(self.commit_url) as response:
                commit_dict = await response.json()
                try:
                    self.files_raw_url = [(x["raw_url"], x["filename"]) for x in commit_dict["files"]]
                except KeyError:
                    self.files_raw_url = []
        except asyncio.TimeoutError:
            pass

    async def get_raw_content(self):
        for raw_url in self.files_raw_url:
            if not self.file_ext_blacklist(raw_url[1]):
                try:
                    async with self.session.get(raw_url[0]) as response:
                        try:
                            self.files_raw_data.append((await response.text(), raw_url[1]))
                        except UnicodeDecodeError:
                            pass
                except (asyncio.TimeoutError, TypeError):
                    APP_LOGGER.warning("Dropped raw url: %s filename: %s", raw_url[0], raw_url[1])

    @staticmethod
    def file_ext_blacklist(filename):
        blacklist = [".jpg", ".gif", ".psd", ".pdf", ".jpeg", ".png", ".webp"]

        if path.splitext(filename)[1] in blacklist:
            return True

        return False
