"""
Handles communication with the gitlab server to get latest events
"""

from typing import Dict

from infobserve.sources.base import SourceBase
from infobserve.common.config import MissingOptionError
from infobserve.common.logger import APP_LOGGER

class GitlabSource(SourceBase):
    def __init__(self, gitlab_config: Dict, name: str = None):
        self.name = name

        self.SOURCE_TYPE = "gitlab"
        self._host = gitlab_config.get("host", "https://gitlab.com")

        self._token = gitlab_config.get("access_token")
        if not self._token:
            APP_LOGGER.fatal("Gitlab source requested but no access token provided")
            raise MissingOptionError("No gitlab access token provided. Go to {} to generate one. See README for more "
                                     "information".format(self._host + "/profile/personal_access_tokens"))