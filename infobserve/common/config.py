""" Contains the config Config class """
import yaml

from .cli_parser import CLI_ARGS


class Config():
    """Infobserver's configuration loader!

    Attributes:
        YARA_RULES_PATHS (list of str): Contains the paths that yara will search for rules.
        YARA_EXTERNAL_VARS (dict): Contains external variables that yara can use.
        GLOBAL_SCRAPE_INTERVAL (int): The global interval that infobserve will set in a source producer.
        PROCESSING_QUEUE_SIZE (int): The max size the processing queue can reach.
        LOGGING_LEVEL (str): The minimum level the logger will emmit messages.
        SOURCES (dict): A dictionary of dictionaries with the configuration of each source.
        DB_CONFIG (dict): A connection pool for the postgresql db server.
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
        self.DB_CONFIG = yaml_file.get("postgres")
        self.REDIS_CONFIG = yaml_file.get("redis", None)

        if yaml_file.get("sources"):
            self.SOURCES = self._source_configs(yaml_file.get("sources"))

    def _source_configs(self, sources):
        list_sources = list()
        for source, configs in sources.items():
            configs["type"] = source
            if configs.get("scrape_interval"):
                configs["timeout"] = configs.get("scrape_interval")
            else:
                configs["timeout"] = self.GLOBAL_SCRAPE_INTERVAL
            list_sources.append(configs)

        return list_sources


CONFIG = Config(CLI_ARGS.get_argument("config"))
