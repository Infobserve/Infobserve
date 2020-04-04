"""The abstract representation of a match"""
from infobserve.matches.ascii_match import AsciiMatch


class Match():

    def __init__(self, yara_match):
        """The MatchBase constructor.

        Arguments:
            yara_match (yara.Match): A yara match object as returned by Yara.Rules.match. It contains the following
        Attributes:
            match_id (int): The id of the ProcessedEvent the Match references.
            event_id (int): The id of the Match in the database.
            rule_matched (str): The rule that matched
            tags_matched (list(str)): A list with the tags of matched rule
            ascii_matches (list(infobserve.matches.AsciiMatches))
        """
        self.match_id = None
        self.event_id = None
        self.rule_matched = yara_match.rule
        self.tags_matched = yara_match.tags
        self.ascii_matches = Match._create_ascii_matches(yara_match.strings)

    def set_match_id(self, match_id):
        """Setter method for the match_id.

        Assigns the values to the related AsciiMatches also.
        Arguments:
            match_id (int): The id of the Match object in the database table.
        """
        self.match_id = match_id
        for ascii_match in self.ascii_matches:
            ascii_match.match_id = match_id

    @staticmethod
    def _create_ascii_matches(strings):
        """Construct the list of AsciiMatch objects.

        The strings return from the yara.Match object are a list of tuples with the following values
        (line, 'string identifier eg '$a', 'actual string').
        Arguments:
            strings (list(str)): A list of the strings matches from the yara.Match object.

        Returns:
            ascii_matches (list(infobserve.matches.AsciiMatches)): A list of the AsciiMatches objects.
        """
        ascii_matches = list()
        for string in strings:
            ascii_matches.append(AsciiMatch(string[2].decode('UTF-8')))

        return ascii_matches

    @staticmethod
    def _create_binary_matches():
        raise NotImplementedError
