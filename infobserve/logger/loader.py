"""This module contains the logger Loader class.

The Loader is used to instantiate a centralized logging configuration for the
loggers used in the application.
"""

import logging
from infobserve.config import CONFIG


class Loader():
    """Infobserver's logger loader!

    Attributes:
        APP_LOGGER (logger): The configured logger of the app
    """

    def __init__(self):
        """

        The __init__ method of the Loader class.

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
