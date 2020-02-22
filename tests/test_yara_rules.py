from pathlib import Path

import plyara
import pytest
import yara


def resolve_rule_files(rule_files):
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


def filter_metadata(metadata):
    if "test_match_1" in metadata.keys():
        return True

    return False


@pytest.mark.parametrize("yara_rule_file", resolve_rule_files(["yara-rules/**/*.yar"]))
def test_match_yara_rules(yara_rule_file):
    parser = plyara.Plyara()

    with open(yara_rule_file) as file:

        parsed_rules = parser.parse_string(file.read())
        compiled_rules = yara.compile(yara_rule_file)

        for rule in parsed_rules:

            filtered_metadata = [d["test_match_1"] for d in rule["metadata"] if d.get("test_match_1")]
            match = compiled_rules.match(data=filtered_metadata[0])
            assert rule.get("rule_name") == match[0].rule
