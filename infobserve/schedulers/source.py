from infobserve.common import APP_LOGGER
from infobserve.sources.factory import SourceFactory


class SourceScheduler():
    """Schedules the Sources in the event loop.

    Attributes:
        sources (list(infobserve.sources.BaseSource)): A list of the configured Sources
        sources_queue (infobserve.common.ProcessingQueue): The queue Sources throw their events.
    """

    def __init__(self, sources_queue, sources=None):
        self.sources = self._init_sources(sources)
        self.sources_queue = sources_queue

    @staticmethod
    def _init_sources(config):
        """ Initiatize Source Objects.

        Arguments:
            config (list of dicts): The configuration dictionaries of the sources.
        """
        source_factory = SourceFactory()
        sources = list()
        for conf_source in config:
            APP_LOGGER.debug("Configured Sources:%s", conf_source)
            sources.append(source_factory.get_source(conf_source))
        return sources

    def schedule(self, loop):
        """ Creates tasks of the fetch_events_scheduled callable.

        Arguments:
            loop (asyncio.AbstractEventLoop): The event loop the tasks will be scheduled to.
        Returns
            loop (asyncio.AbstractEventLoop): The event loop with the tasks created.
        """
        for source in self.sources:
            APP_LOGGER.debug("Scheduling Source:%s", source.name)
            loop.create_task(source.fetch_events_scheduled(self.sources_queue))

        return loop
