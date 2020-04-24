"""
Handles communication with the gitlab server to get latest events
"""

from typing import Dict

from infobserve.sources.base import SourceBase

class GitlabSource(SourceBase):
    def __init__(self, gitlab_config: Dict, name: str = None):
        self.name = name

        self.SOURCE_TYPE = "gitlab"
        self._host = gitlab_config.get("host")