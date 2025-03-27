from griptape.mixins.rule_mixin import RuleMixin
from griptape.rules import JsonSchemaRule, Rule, Ruleset
from griptape.structures import Agent
from griptape.tasks import PromptTask


class TestRuleMixin:
    def test_no_rules(self):
        assert RuleMixin()

    def test_rules(self):
        rule = Rule("foo")
        mixin = RuleMixin(rules=[rule])

        assert mixin.rules == [rule]

    def test_rulesets(self):
        ruleset = Ruleset("foo", [Rule("bar")])
        mixin = RuleMixin(rulesets=[ruleset])

        assert mixin.rulesets == [ruleset]
        mixin.rulesets.append(Ruleset("baz", [Rule("qux")]))
        assert mixin.rulesets == [ruleset]

    def test_rules_and_rulesets(self):
        mixin = RuleMixin(rules=[Rule("foo")], rulesets=[Ruleset("bar", [Rule("baz")])])

        assert mixin.rules == [Rule("foo")]
        assert mixin.rulesets[0].name == "bar"
        assert mixin.rulesets[0].rules == [Rule("baz")]
        assert mixin.rulesets[1].name == "Default Ruleset"
        assert mixin.rulesets[1].rules == [Rule("foo")]

    def test_inherits_structure_rulesets(self):
        # Tests that a task using the mixin inherits rulesets from its structure.
        ruleset1 = Ruleset("foo", [Rule("foo rule")])
        ruleset2 = Ruleset("bar", [Rule("bar rule")])

        agent = Agent(rulesets=[ruleset1])
        task = PromptTask(rulesets=[ruleset2])
        agent.add_task(task)

        assert task.rulesets == [ruleset1, ruleset2]

    def test_to_dict(self):
        mixin = RuleMixin(
            rules=[
                Rule("foo"),
                JsonSchemaRule(
                    {
                        "type": "object",
                        "properties": {
                            "foo": {"type": "string"},
                        },
                        "required": ["foo"],
                    }
                ),
            ],
            rulesets=[Ruleset("bar", [Rule("baz")])],
        )

        assert mixin.to_dict() == {
            "rulesets": [
                {
                    "id": mixin.rulesets[0].id,
                    "meta": {},
                    "name": "bar",
                    "rules": [{"type": "Rule", "value": "baz"}],
                    "type": "Ruleset",
                },
            ],
            "rules": [
                {"type": "Rule", "value": "foo"},
                {
                    "type": "JsonSchemaRule",
                    "value": {
                        "properties": {"foo": {"type": "string"}},
                        "required": ["foo"],
                        "type": "object",
                    },
                },
            ],
            "type": "RuleMixin",
        }

    def test_from_dict(self):
        mixin = RuleMixin(
            rules=[
                Rule("foo"),
                JsonSchemaRule(
                    {
                        "type": "object",
                        "properties": {
                            "foo": {"type": "string"},
                        },
                        "required": ["foo"],
                    }
                ),
            ],
            rulesets=[Ruleset("bar", [Rule("baz")])],
        )

        new_mixin = RuleMixin.from_dict(mixin.to_dict())

        for i, _ in enumerate(new_mixin.rulesets):
            rules = mixin.rulesets[i].rules
            new_rules = new_mixin.rulesets[i].rules
            for j, _ in enumerate(rules):
                assert rules[j].value == new_rules[j].value
                assert rules[j].meta == new_rules[j].meta
