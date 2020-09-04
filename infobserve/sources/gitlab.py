"""
Handles communication with the gitlab server to get latest events
"""
import re

import aiohttp

import infobserve.sources.git.utils
import infobserve.sources.git.git_events
from infobserve.common.logger import APP_LOGGER

from typing import Dict

from infobserve.sources.base import SourceBase

class GitlabSource(SourceBase):
    def __init__(self, gitlab_config: Dict, name: str = None):
        SourceBase.__init__(self, name)
        self.SOURCE_TYPE = "gitlab"

        if not re.match("https?://", gitlab_config.get("host")):
            APP_LOGGER.info("No http scheme for gitlab host. Assuming HTTPS")
            self._host = f'https://{gitlab_config.get("host")}'
        else:
            self._host = gitlab_config.get("host")

        self._project_id = gitlab_config.get("project_id")
        self._request_header = {
            "SECRET-TOKEN": gitlab_config.get("access_token")
        }
        self._events_url = f'{self._host}/api/v4/projects/{self._project_id}/events'

    async def fetch_events(self):
        since = infobserve.sources.git.utils.get_date()

        async with aiohttp.ClientSession() as session:
            async with session.get(self._events_url, headers=self._request_header) as resp:
                events = await resp.json()