from unittest.mock import patch

import plyara
import pytest
import yara

from infobserve.processors.yara_processor import YaraProcessor


def get_mocked_yaraprocessor():
    """ Returns
    """
    with patch.object(YaraProcessor, "__init__", lambda x: None):
        processor = YaraProcessor()  # pylint: disable=E1120
        return processor


def filter_metadata(metadata):
    if "test_match_1" in metadata.keys():
        return True

    return False


@pytest.mark.parametrize("yara_rule_file", get_mocked_yaraprocessor()._get_file_sources(["yara-rules/**/*.yar"]))
def test_match_yara_rules(yara_rule_file):
    parser = plyara.Plyara()

    with open(yara_rule_file) as file:

        parsed_rules = parser.parse_string(file.read())
        compiled_rules = yara.compile(yara_rule_file)

        for rule in parsed_rules:

            filtered_metadata = [d["test_match_1"] for d in rule["metadata"] if d.get("test_match_1")]
            match = compiled_rules.match(data=filtered_metadata[0])
            assert rule.get("rule_name") == match[0].rule
