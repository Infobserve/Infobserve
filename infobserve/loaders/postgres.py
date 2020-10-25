""" This module contains the PgLoader class."""
from infobserve.common import APP_LOGGER
from infobserve.common.pool import PgPool


class PgLoader():
    """ProcessedEvent object consumer stores them into the Pgsql database.

    Attributes:
        _processing (boolean): Indicates if the PgLoader instance consumes a Queue.
        pool (infobserve.common.pool.Pool): The pool that connections will be acquired.
        consume_queue (infobserve.common.queue.ProcessingQueue): The queue ProcessedEvent object will be consumed from.
    """

    def __init__(self, consume_queue):
        """
        Args:
            consume_queue (infobserve.processing.queue.ProcessingQueue):
                        An instance of the queue in which ProcessedEvent objects will
                        be retrieved.
        """
        self._processing = False
        self.pool = PgPool()
        self.consume_queue = consume_queue

    async def process(self):
        """Start Consuming the `consume_queue`.

        This function loops endlessly fetching ProcessedEvent objects
        and inserting them into the database along with the insertions of the
        Match and AsciiMatch objects they contain.
        """
        self._processing = True

        while True:
            processed_event = await self.consume_queue.get_event()
            event_id = await self._insert_event(processed_event)
            processed_event.set_event_id(event_id)
            for match in processed_event.matches:
                match_id = await self._insert_match(match)
                match.set_match_id(match_id)
                for ascii_match in match.ascii_matches:
                    await self._insert_ascii_match(ascii_match)

            APP_LOGGER.debug("Inserted event from %s source. Rule files matched: %s", processed_event.source,
                             ", ".join(processed_event.get_rules_matched()))

    @staticmethod
    async def _insert_event(processed_event):
        """Insert an Event into the database.

        Arguments:
            processed_event (infobserve.events.processed.ProcessedEvent): The processed event that will be inserted

        Returns:
            id (int): The id of the inserted ProcessedEvent.
        """
        async with PgPool().acquire() as conn:
            res = await conn.fetch(
                '''INSERT INTO EVENTS (source, raw_content, filename, creator, time_created, time_discovered)
                VALUES ($1, $2, $3, $4, $5, $6) RETURNING id;''', processed_event.source, processed_event.raw_content,
                processed_event.filename, processed_event.creator, processed_event.timestamp,
                processed_event.time_discovered)
            APP_LOGGER.debug("Inserted Event with id:%s", res[0]["id"])

            return res[0]["id"]

    @staticmethod
    async def _insert_match(match):
        """Insert an Event into the database.

        Arguments:
            match (infobserve.matches.match.Match): The match object that will be inserted.

        Returns:
            id (int): The id of the inserted Match
        """
        async with PgPool().acquire() as conn:
            res = await conn.fetch(
                '''INSERT INTO MATCHES (event_id, rule_matched, tags_matched) VALUES ($1, $2, $3) RETURNING id;''',
                match.event_id, match.rule_matched, match.tags_matched)

            return res[0]["id"]

    @staticmethod
    async def _insert_ascii_match(ascii_match):
        """Insert an AsciiMatch into the database.

        Arguments:
            ascii_match (infobserve.matches.match.Match): The AsciiMatch object that will be inserted.

        Returns:
            id (int): The id of the inserted AsciiMatch
        """
        async with PgPool().acquire() as conn:
            res = await conn.fetch(
                '''INSERT INTO ASCII_MATCH (match_id, matched_string) VALUES ($1, $2) RETURNING id;''',
                ascii_match.match_id, str(ascii_match.matched_string))

            return res[0]["id"]
