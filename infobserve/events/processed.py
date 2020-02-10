"""This module contains the ProcessedEvent class definition."""
from datetime import datetime

from infobserve.matches.match import Match

from .base import BaseEvent


class ProcessedEvent(BaseEvent):
    """This class represents an event after it has been processed.

    Attributes:
        event_id (int): The id of the ProcessedEvent in the database.
        raw_content (str): The whole text of the event
        filename (str): The name the file the event was taken from.
        creator (str): The user that is responsible for the event.
        time_discovered (datetime): The time the event was processed.
        matches (list(infobserve.matches.Match)): A list of the matches that fired up the YaraRules.
    """

    def __init__(self, unprocessed, matches):
        """The constructor.

        Arguments:
            unprocessed (infobserve.event.Event): An event object straight from a Source Producer Queue.
            matches (yara.Match): All the matches that triggered Yara Rules.
        """
        super().__init__(unprocessed.timestamp, source=unprocessed.source)
        self.event_id = None
        self.raw_content = unprocessed.raw_content
        self.filename = unprocessed.filename
        self.creator = unprocessed.creator
        self.time_discovered = datetime.now()
        self.matches = self._build_matches(matches)

    def _build_matches(self, matches):
        """Construct the list of Match objects.

        Arguments:
            strings (list(str)): A list of the strings that matched.

        Returns:
            matches_list (list(infobserve.matches.Match)): A list of the Match objects.
        """
        matches_list = list()
        for match in matches:
            matches_list.append(Match(match))
        return matches_list

    def set_event_id(self, event_id):
        """Setter method for the event_id.

        Assigns the values to the related Match objects also.
        Arguments:
            event (int): The id of the ProcessedEvent object in the database table.
        """
        self.event_id = event_id
        for match in self.matches:
            match.event_id = event_id

    async def get_raw_content(self):
        return self.raw_content
