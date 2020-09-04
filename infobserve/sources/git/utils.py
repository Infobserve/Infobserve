import re
import datetime

from typing import Dict

from infobserve.common.logger import APP_LOGGER


class UnparseableLinkHeader(Exception):
    pass


def get_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")

def parse_link(link: str) -> Dict:
    ret = {}
    parts = link.split(', ')
    for part in parts:
        rel_link, rel = part.split('; ')
        rel = rel.replace('rel=', '').strip('"')
        match = re.match(r'^\s*<(.*?)>', rel_link)
        if not match or not len(match.group) == 1:
            APP_LOGGER.critical('Unable to parse Link header %s (%s=%s)',
                                link,rel, rel_link)
            raise UnparseableLinkHeader('Could not parse Link header')

        ret[rel] = match.group(1)

    return ret
