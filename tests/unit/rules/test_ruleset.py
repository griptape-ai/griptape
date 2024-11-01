import os
from pathlib import Path

import pytest

from griptape.drivers import LocalRulesetDriver
from griptape.rules import Rule, Ruleset

TEST_RULESET_DIR = str(Path(os.path.dirname(__file__), "../../resources/"))
TEST_RULESET_NAME = "test_ruleset.json"


class TestRuleset:
    @pytest.fixture()
    def driver(self):
        return LocalRulesetDriver(persist_dir=TEST_RULESET_DIR)

    def test_init(self):
        ruleset = Ruleset("foobar", rules=[Rule("rule1"), Rule("rule2")])

        assert ruleset.name == "foobar"
        assert len(ruleset.rules) == 2

    def test_from_driver(self, driver):
        ruleset = Ruleset(
            name=TEST_RULESET_NAME,
            rules=[Rule("rule1"), Rule("rule2")],
            meta={"key": "value"},
            ruleset_driver=driver,
        )

        assert len(ruleset.rules) == 4
        assert ruleset.meta == {"foo": "bar", "key": "value"}
        assert ruleset.rules[0].value == "value1"
        assert ruleset.rules[3].value == "rule2"
