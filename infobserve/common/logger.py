"""This module contains the Logger class.

The Logger is used to instantiate a centralized logging configuration for the
loggers used in the application.
"""

import logging

from .config import CONFIG


class Logger():
    """Infobserver's Logger!

    Attributes:
        APP_LOGGER (logger): The configured logger of the app
    """

    def __init__(self):
        """

        The __init__ method of the Logger class.

        Configures the application logger and assigns the configured logger
        in an attribute APP_LOGGER
        """

        self.logger = logging.getLogger("infobserver")
        self.logger.setLevel(CONFIG.LOGGING_LEVEL)

        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s')
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(CONFIG.LOGGING_LEVEL)
        consoleHandler.setFormatter(formatter)
        self.logger.addHandler(consoleHandler)

    def get_logger(self):
        """Returns the application logger."""
        return self.logger


APP_LOGGER = Logger().get_logger()
