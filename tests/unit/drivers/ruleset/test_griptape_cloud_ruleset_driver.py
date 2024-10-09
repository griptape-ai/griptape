import pytest

from griptape.drivers import GriptapeCloudRulesetDriver
from griptape.rules import Rule


class TestGriptapeCloudRulesetDriver:
    @pytest.fixture(autouse=True)
    def _mock_requests(self, mocker):
        mocker.patch("requests.get")

        def get(*args, **kwargs):
            if "rules?ruleset_id=" in str(args[1]):
                ruleset_id = args[1].split("=")[-1]
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {
                        "rules": [
                            {
                                "rule_id": f"{ruleset_id}_rule",
                                "rule": "test rule value",
                                "metadata": {"foo": "bar"},
                            }
                        ]
                    }
                    if ruleset_id != "no_rules"
                    else {"rules": []},
                    status_code=200,
                )
            elif "/rulesets/" in str(args[1]):
                ruleset_id = args[1].split("/")[-1]
                return mocker.Mock(
                    # raise for status if ruleset_id is == not_found
                    raise_for_status=lambda: None if ruleset_id != "not_found" else ValueError,
                    json=lambda: {
                        "metadata": {"foo": "bar"},
                        "name": "test",
                        "ruleset_id": ruleset_id,
                    },
                    status_code=200 if ruleset_id != "not_found" else 404,
                )
            elif "/rulesets?alias=" in str(args[1]):
                alias = args[1].split("=")[-1]
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {"rulesets": [{"ruleset_id": alias, "alias": alias, "metadata": {"foo": "bar"}}]}
                    if alias != "not_found"
                    else {"rulesets": []},
                    status_code=200,
                )
            else:
                return mocker.Mock()

        mocker.patch(
            "requests.request",
            side_effect=get,
        )

    @pytest.fixture()
    def ruleset_driver(self):
        return GriptapeCloudRulesetDriver(api_key="test", raise_not_found=False)

    def test_no_api_key_raises(self):
        with pytest.raises(ValueError):
            GriptapeCloudRulesetDriver(api_key=None)

    def test_no_ruleset_raises(self, ruleset_driver):
        ruleset_driver.raise_not_found = True
        with pytest.raises(ValueError):
            ruleset_driver.load(ruleset_name="not_found")

    def test_no_ruleset_by_id_raises(self, ruleset_driver):
        ruleset_driver.ruleset_id = "not_found"
        ruleset_driver.raise_not_found = True
        with pytest.raises(ValueError):
            ruleset_driver.load(ruleset_name="not_found")

    def test_no_ruleset_by_id(self, ruleset_driver):
        ruleset_driver.ruleset_id = "not_found"
        rules, meta = ruleset_driver.load("not_found")
        assert rules == []
        assert meta == {}

    def test_no_ruleset_by_name(self, ruleset_driver):
        rules, meta = ruleset_driver.load(ruleset_name="not_found")
        assert rules == []
        assert meta == {}

    def test_load_by_name(self, ruleset_driver):
        name = "test"
        rules, meta = ruleset_driver.load(ruleset_name=name)
        assert len(rules) == 1
        assert isinstance(rules[0], Rule)
        assert rules[0].value == "test rule value"
        assert rules[0].meta == {"foo": "bar", "griptape_cloud_rule_id": f"{name}_rule"}
        assert meta == {"foo": "bar"}

    def test_load_by_id(self, ruleset_driver):
        ruleset_id = "1234"
        ruleset_driver.ruleset_id = ruleset_id
        rules, meta = ruleset_driver.load("not_found")
        assert len(rules) == 1
        assert isinstance(rules[0], Rule)
        assert rules[0].value == "test rule value"
        assert rules[0].meta == {"foo": "bar", "griptape_cloud_rule_id": f"{ruleset_id}_rule"}
        assert meta == {"foo": "bar"}

    def test_load_by_id_no_rules(self, ruleset_driver):
        ruleset_driver.ruleset_id = "no_rules"
        rules, meta = ruleset_driver.load("not_found")
        assert rules == []
        assert meta == {"foo": "bar"}

    def test_load_by_name_no_rules(self, ruleset_driver):
        rules, meta = ruleset_driver.load(ruleset_name="no_rules")
        assert rules == []
        assert meta == {"foo": "bar"}
