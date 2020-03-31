# pylint: disable=redefined-outer-name
from datetime import datetime
from unittest.mock import patch

import pytest
from aioresponses import aioresponses
from pbwrap.asyncpbwrap import AsyncPaste

from infobserve.events import PasteEvent


@pytest.fixture
def paste():
    return AsyncPaste({
        "scrape_url": "https://scrape.pastebin.com/api_scrape_item.php?i=0CeaNm8Y",
        "full_url": "https://pastebin.com/0CeaNm8Y",
        "date": "1442911802",
        "key": "0CeaNm8Y",
        "size": "890",
        "expire": "1442998159",
        "title": "Once we all know when we goto function",
        "syntax": "java",
        "user": "admin"
    })


@pytest.fixture
def paste_event(paste):
    return PasteEvent(paste)


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


def test_paste_event_constructor(paste):
    paste_event = PasteEvent(paste)
    assert paste_event.id == paste.key
    assert paste_event.raw_url == paste.scrape_url
    assert paste_event.timestamp == datetime.fromtimestamp(int(paste.date))


@pytest.mark.asyncio
async def test_get_raw_content(mock_aioresponse, paste_event):

    def custom_event(x):
        return "KappaKeepo"

    with patch.object(AsyncPaste, "scrape_raw_text", custom_event):
        text = await paste_event.get_raw_content()
    assert text == "KappaKeepo"
