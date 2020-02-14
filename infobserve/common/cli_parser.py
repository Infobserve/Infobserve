"""
Class that parses and merges cli arguments with default values
"""

import argparse
from pathlib import Path


class Parser:
    DEFAULT_CONF_PATH = "config.yaml"

    def __init__(self):
        self._args = {}
        self._parse()

    def _parse(self):
        """
        Parses cli arguments and stores them
        """

        parser = argparse.ArgumentParser()

        parser.add_argument("--config", "-c", dest="config", type=Path,
                            help="The path to the configuration YAML file")

        cli_args = parser.parse_args()

        self._args["config"] = cli_args.config if cli_args.config else Parser.DEFAULT_CONF_PATH

    def get_args(self):
        return self._args

    def get_argument(self, arg):
        try:
            return self._args[arg]
        except KeyError:
            raise KeyError("Requested argument ({}) never parsed by cli parser".format(arg))


CLI_ARGS = Parser()
