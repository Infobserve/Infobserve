"""
This module handles the recursive scraping of a gitlab repository
"""
import re
from typing import List, Optional
from pprint import PrettyPrinter

import aiohttp

from infobserve.common.logger import APP_LOGGER


# TODO: This needs to be put in another module
class Http401Unauthorized(Exception):
    pass


LINK_PAGES = r".*<(.*)>;\srel=\"next\",\s"



class RepositoryScraper:

    def __init__(self, host: str, access_token: str, project_id: str, ignored: List[str]):
        self._root_uri = "{}/api/v4/projects/{}/repository/".format(host, project_id)
        self._access_token = access_token
        self._ignored = ignored
        self._project_id = project_id

    async def walk(self) -> List[str]:
        """
        Asynchronously scrapes a gitlab repository, yielding each non-ignored file encountered

        Yields:
            A string containing the raw content of each file
        """

        blobs: List[str] = []
        next_uri: Optional[str] = self._root_uri + "tree?recursive=true&page=0&per_page=20"

        async with aiohttp.ClientSession() as session:
            while next_uri:
                resp = await session.get(next_uri)
                resp_files = await resp.json()

                if isinstance(resp_files, dict) and "message" in resp_files:
                    if resp_files["message"] == "401 Unauthorized":
                        raise Http401Unauthorized

                for resp_file in resp_files:
                    if resp_file == "error":
                        print("error for path " + next_uri)

                    if self._is_ignored(resp_file["path"]):
                        continue

                    if resp_file["type"] != "blob":
                        # This should never occur with the `?recursive=True` argument
                        # Due to the "?recursive=true" GET argument, we do not care about non-blob items (like trees),
                        # we will see them later
                        continue
                    blobs.append(resp_file["id"])

                if "link" in resp.headers:
                    link_header = resp.headers["link"]
                    print(link_header + "\n\n")
                    link_match = re.search(LINK_PAGES, link_header)
                    if link_match is None:
                        next_uri = None
                    else:
                        next_uri = link_match.group(1)
                else:
                    # We should have stopped looping when no "next" link was present
                    APP_LOGGER.critical("No 'link' in response header for call to %s", next_uri)
                    raise ValueError

        APP_LOGGER.debug("The repository %s contained %s non-ignored files", self._project_id, len(blobs))
        return blobs

    async def get_raw_blob(self, sha: str):
        """
        Makes a gitlab API call to resolve the provided sha

        Args:
            sha: The SHA for the blob as returned by the `walk` method
        Returns:
            A string containing the resolved raw content of the blob
        """
        blob_uri = self._root_iro + "blobs/{}/raw".format(sha)

        async with aiohttp.ClientSession() as session:
            pass

    def _is_ignored(self, filename: str):
        """
        Tests whether the provided file should be included

        Args:
            filename: The full path to a file
        Returns:
            True if the file should be ignored
        """
        for rule in self._ignored:
            if re.match(rule, filename):
                APP_LOGGER.debug("Ignoring file '%s' because it matched '%s'", filename, rule)
                return True
        return False
