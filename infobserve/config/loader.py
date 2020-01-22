""" Contains the config Loader class """

import yaml


class Loader():
    """Infobserver's configuration loader!

    Attributes:
        YARA_RULES_PATHS (list of str): Contains the paths that yara will search for rules.
        YARA_EXTERNAL_VARS (dict): Contains external variables that yara can use.
        GLOBAL_SCRAPE_INTERVAL (int): The global interval that infobserve will set in a source producer.

    """

    def __init__(self, config_file="config.yaml"):
        """

        The __init__ method of the Loader class.

        Loads the configuration from a yaml file or from sensible default values.

        Args:
            config_file (str): The path of the configuration yaml.

        """
        try:
            with open(config_file) as file:
                yaml_file = yaml.load(file, Loader=yaml.FullLoader)

        except FileNotFoundError:
            yaml_file = dict()

        self.GLOBAL_SCRAPE_INTERVAL = yaml_file.get("global_scrape_interval", 60)  # In Seconds
        self.YARA_RULES_PATHS = yaml_file.get("yara_rules_paths", "yara/*.yar")
        self.YARA_EXTERNAL_VARS = yaml_file.get("yara_external_vars", None)
        self.PROCESSING_QUEUE_SIZE = yaml_file.get("processing_queue_size", 0)
        self.LOGGING_LEVEL = yaml_file.get("log_level", "DEBUG")

        # Think of a way to express this in more elegant and dynamic fashion
        # Factory Pattern for the Sources for easy extendability.
        if yaml_file.get("sources", None):
            sources_dict = yaml_file["sources"]

            if sources_dict.get("gist", None):
                self.SOURCE_GIST_CONF = sources_dict["gist"]
            else:
                self.SOURCE_GIST_CONF = None
