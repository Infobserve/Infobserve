from unittest.mock import Mock
from datetime import datetime
import pytest

from infobserve.events import ProcessedEvent, GistEvent


@pytest.fixture
def processed_event():
    mocked_unprocessed_event = Mock()
    mocked_unprocessed_event.source = "example"
    mocked_unprocessed_event.timestamp = datetime(2020, 5, 22)
    mocked_unprocessed_event.raw_content = "Dummy Content"

    mocked_matches = ["match1", "match2", "match3"]
    return ProcessedEvent(mocked_unprocessed_event, mocked_matches)
