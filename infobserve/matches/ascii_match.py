"""This module contains the AsciiMatch class"""


class AsciiMatch():
    """The ascii text that references a Match object.

    Attributes:
        id (int): The id of the AsciiMatch row in the db table.
        match_id(int): The match_id that this AsciiMatch references in the database.
        matched_string(str): A string that triggered the yara rule
    """

    def __init__(self, string):
        """The constructor.

        Arguments:
            string (str): Just a str!
        """
        self.id = None
        self.match_id = None
        self.matched_string = string
