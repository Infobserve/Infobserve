# pylint: disable=redefined-outer-name
from unittest.mock import Mock
from datetime import datetime
import pytest

from infobserve.events import ProcessedEvent


@pytest.fixture
def mocked_match():
    match = Mock()
    match.rule = "Example Rule"
    match.tags = ["tag1", "tag2"]
    match.strings = [('81L', "$a", b"String1"), ('82L', "$b", b"String2")]
    return match


@pytest.fixture
def processed_event(mocked_match):
    mocked_unprocessed_event = Mock()
    mocked_unprocessed_event.source = "example"
    mocked_unprocessed_event.timestamp = datetime(2020, 5, 22)
    mocked_unprocessed_event.raw_content = "Dummy Content"

    mocked_matches = [mocked_match]
    return ProcessedEvent(mocked_unprocessed_event, mocked_matches)


def test_set_event_id(processed_event):
    processed_event.set_event_id(1)
    assert processed_event.event_id == 1


def test_get_rules_matched(processed_event):
    rules = processed_event.get_rules_matched()
    assert rules == ["Example Rule"]
