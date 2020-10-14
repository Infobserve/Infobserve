"""The implementation of the GithubEvent Class."""
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
            github_event (dict): A complex dictionary returned by the Github API.
            session (aiohttp.Session): Session of aiohttp to create the commits list.
        """
        BaseEvent.__init__(self, github_event.get("created_at"), source="github-public-events")

        self.id = github_event.get("id")
        self.creator = github_event["actor"].get("login")
        self.commits = [Commit(x, session) for x in github_event["payload"]["commits"]]
        self.session = session

    async def get_raw_content(self):
        """Retrieves the raw content of all the commits in GithubEvent.
        """
        for commit in self.commits:
            await commit.get_commit_raw_urls()
            await commit.get_raw_content()

    def commit_raw_content(self):
        for commit in self.commits:
            for raw_data in commit.files_raw_data:
                yield CommitEvent(self, raw_data[0], raw_data[1])


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
                    APP_LOGGER.warning("No 'files' key in commit: %s", self.commit_url)
                    self.files_raw_url = []
        except asyncio.TimeoutError:
            APP_LOGGER.warning("Dropped commit url: %s", self.commit_url)

    async def get_raw_content(self):
        for raw_url in self.files_raw_url:
            if not self.file_ext_blacklist(raw_url[1]):
                try:
                    async with self.session.get(raw_url[0]) as response:
                        try:
                            self.files_raw_data.append((await response.text(), raw_url[1]))
                        except UnicodeDecodeError:
                            APP_LOGGER.warning("Unicode Decoding error in filename:%s", raw_url[1])
                except (asyncio.TimeoutError, TypeError):
                    APP_LOGGER.warning("Dropped raw url: %s filename: %s", raw_url[0], raw_url[1])

    @staticmethod
    def file_ext_blacklist(filename):
        blacklist = [
            ".jpg", ".gif", ".psd", ".pdf", ".jpeg", ".png", ".webp", ".pyc", ".sqlite3", ".woff", ".ttf", ".woff2",
            ".zip", ".gz", ".h5"
        ]

        return path.splitext(filename)[1] in blacklist


class CommitEvent(BaseEvent):
    """The CommitEvent Class represents a file changed in a commit that belongs to a GitHubEvent"""

    def __init__(self, github_event: GithubEvent, raw_content: str, filename: str):
        """Instantiates the CommitEvent.

        Arguments:
            github_event (GithubEvent): The GithubEvent object the commit belongs to.
            raw_content (str): The content of the file changed in str.
            filename (str): The filename of the file changed
        """
        BaseEvent.__init__(self, github_event.timestamp, source=github_event.source)
        self.id: str = github_event.id
        self.creator: str = github_event.creator
        self.raw_content: str = raw_content
        self.filename: str = filename

    async def get_raw_content(self):
        return self.raw_content

    def is_valid(self):
        if self.raw_content:
            return True

        return False
