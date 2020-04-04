# pylint: disable=redefined-outer-name
from unittest.mock import patch

import aiohttp.test_utils
import pytest
from aioresponses import aioresponses

from infobserve.events import GistEvent

RAW_GIST = {
    "url": "https://api.github.com/gists/aa5a315d61ae9438b18d",
    "forks_url": "https://api.github.com/gists/aa5a315d61ae9438b18d/forks",
    "commits_url": "https://api.github.com/gists/aa5a315d61ae9438b18d/commits",
    "id": "aa5a315d61ae9438b18d",
    "node_id": "MDQ6R2lzdGFhNWEzMTVkNjFhZTk0MzhiMThk",
    "git_pull_url": "https://gist.github.com/aa5a315d61ae9438b18d.git",
    "git_push_url": "https://gist.github.com/aa5a315d61ae9438b18d.git",
    "html_url": "https://gist.github.com/aa5a315d61ae9438b18d",
    "files": {
        "hello_world.rb": {
            "filename":
                "hello_world.rb",
            "type":
                "application/x-ruby",
            "language":
                "Ruby",
            "raw_url":
                "https://gist.githubusercontent.com/octocat/6cad326836d38bd3a7ae/raw/db9c55113504e46fa076e7df3a04ce592e2e86d8/hello_world.rb",
            "size":
                167
        }
    },
    "public": True,
    "created_at": "2010-04-14T02:15:15Z",
    "updated_at": "2011-06-20T11:34:15Z",
    "description": "Hello World Examples",
    "comments": 0,
    "user": None,
    "comments_url": "https://api.github.com/gists/aa5a315d61ae9438b18d/comments/",
    "owner": {
        "login": "octocat",
        "id": 1,
        "node_id": "MDQ6VXNlcjE=",
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "gravatar_id": "",
        "url": "https://api.github.com/users/octocat",
        "html_url": "https://github.com/octocat",
        "followers_url": "https://api.github.com/users/octocat/followers",
        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
        "organizations_url": "https://api.github.com/users/octocat/orgs",
        "repos_url": "https://api.github.com/users/octocat/repos",
        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
        "received_events_url": "https://api.github.com/users/octocat/received_events",
        "type": "User",
        "site_admin": False
    },
    "truncated": False
}


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.fixture
def gist_event():
    return GistEvent(RAW_GIST)


def test_constructor(gist_event):
    assert gist_event.creator == RAW_GIST["owner"]["login"]
    assert gist_event.id == RAW_GIST["id"]
    assert gist_event.raw_url == RAW_GIST["files"]["hello_world.rb"]["raw_url"]
    assert gist_event.filename == RAW_GIST["files"]["hello_world.rb"]["filename"]
    assert gist_event.size == RAW_GIST["files"]["hello_world.rb"]["size"]


def test_gist_event_is_valid():
    with patch.object(GistEvent, "__init__", lambda x: None):
        gist = GistEvent()  # pylint: disable=E1120
        gist.raw_url = None
        assert not gist.is_valid()
        gist.raw_url = "https://gist.githubusercontent.com/octocat/6cad326e/raw/db9c5511350ce592e2e86d8/hello_world.rb"
        assert gist.is_valid()


@pytest.mark.asyncio
async def test_get_raw_content(mock_aioresponse, gist_event):
    custom_text = "KappaKeepo"
    mock_aioresponse.get(gist_event.raw_url, body=custom_text, status=200)
    async with aiohttp.ClientSession() as session:
        text = await gist_event.get_raw_content(session)
        assert text == "KappaKeepo"


@pytest.mark.asyncio
async def test_get_raw_content_unicode_error(mock_aioresponse, gist_event):
    custom_text = b"kapsdsd\xffdsdsds"
    mock_aioresponse.get(gist_event.raw_url, body=custom_text, status=200)
    async with aiohttp.ClientSession() as session:
        text = await gist_event.get_raw_content(session)
        assert text is None
