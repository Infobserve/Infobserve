from pathlib import Path

import yara
from infobserve.logger import APP_LOGGER


# TODO: Add exception handlers. Async functions don't notify anyone
#       when they fail, so the whole script hangs


class YaraProcessor:
    """
    Consumes Sources from the Processing queue, passes them through the
    Yara matching engine and adds them to the DB Queue (TBI)
    """
    def __init__(self, rule_files, source_queue, db_queue):
        """
        Args:
            rule_files (list): A list of paths to the Yara rule files
                               Each item can contain wildcards.
            source_queue (infobserve.processing.queue.ProcessingQueue):
                        An instance of the queue in which Source objects will
                        be retrieved from
            db_queue (infobserve.processing.queue.ProcessingQueue):
                        An instance of the queue in which Event objects will
                        be inserted into
        """
        self._source_queue = source_queue
        self._db_queue = db_queue

        # Generate list of rules along with their namespaces
        self._rules = {
            filepath: filepath
            for filepath
            in self._get_file_sources(rule_files)
        }

        # Is there a point in making `_rules` a class attribute?
        # discuss
        self._engine = yara.compile(filepaths=self._rules)

    async def process(self):
        """
        The consumer function for the source queue.
        Removes Sources from the Processing Queue, tries to match them
        against the provided Yara rules. Places any matches into the Database
        Queue for further processing and storage (TBI - Right now, it simply
        logs matches)
        """
        while True:
            event = await self._source_queue.get_event()

            # Right now `Event.get_contents` does not exist
            # but this should be the way to call it
            matches = self._engine.match(data=event.get_contents())

            for match in matches:
                APP_LOGGER.debug(
                    """
                    ======= Match ======
                    Rule matched: %s
                    Tags: %s
                    Strings: %s
                    """,
                    match.rule, match.tags, match.strings
                )

            self._source_queue.notify()

    def _get_file_sources(self, rule_files):
        """
        Resolves the paths provided in the `rule_files` list. Also expands
        any `*` found in the paths using pathlib.Path

        Args:
            rule_files (list[str]): The list of rule file paths to resolve
        Returns:
            A generator object that yields each resolved path as a string
        """
        for rule_file in rule_files:
            filepath = Path(rule_file)
            if filepath.is_file():
                yield filepath.as_posix()
            else:
                for inner_file in Path().glob(rule_file):
                    yield inner_file.as_posix()
