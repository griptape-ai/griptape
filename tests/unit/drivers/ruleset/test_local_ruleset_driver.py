from pathlib import Path

import pytest

from griptape.drivers import LocalRulesetDriver

TEST_RULESET_DIR = str(Path("tests/resources/"))
TEST_RULESET_NAME = "test_ruleset.json"


class TestLocalRulesetDriver:
    @pytest.fixture()
    def ruleset_driver(self):
        return LocalRulesetDriver(raise_not_found=False, persist_dir=TEST_RULESET_DIR)

    def test_load(self, ruleset_driver):
        rules, meta = ruleset_driver.load("name")
        assert rules == []
        assert meta == {}

    def test_load_raises(self, ruleset_driver):
        ruleset_driver.raise_not_found = True
        with pytest.raises(ValueError):
            ruleset_driver.load("test")

    def test_load_by_persist_dir(self, ruleset_driver):
        rules, meta = ruleset_driver.load(TEST_RULESET_NAME)
        assert len(rules) == 2
        assert rules[0].value == "value1"
        assert rules[0].meta == {"foo": "bar"}
        assert rules[1].value == "value2"
        assert rules[1].meta == {"foo": "baz"}
        assert meta == {"foo": "bar"}

    def test_load_by_name(self, ruleset_driver):
        rules, meta = ruleset_driver.load(TEST_RULESET_NAME)
        assert len(rules) == 2
        assert rules[0].value == "value1"
        assert rules[0].meta == {"foo": "bar"}
        assert meta == {"foo": "bar"}

    def test_load_bad_file(self, ruleset_driver):
        with pytest.raises(ValueError):
            ruleset_driver.load("test.txt")
