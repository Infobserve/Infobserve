import base64
import csv

from infobserve.events import ProcessedEvent


class CsvLoader():
    """ProcessedEvent object consumer stores them in csv format"""
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, path):
        self.path = path

    def write_event(self, event: ProcessedEvent):
        with open(self.path, 'a') as event_log:
            event_writer = csv.writer(event_log)
            event_writer.writerow([
                event.event_id,
                event.source,
                event.time_discovered.strftime(self.TIMESTAMP_FORMAT),
                event.creator,
                event.filename,
                "|".join(event.get_rules_matched()),
                str(base64.b64encode((event.raw_content.encode("utf-8"))).decode("utf-8")),
            ])
