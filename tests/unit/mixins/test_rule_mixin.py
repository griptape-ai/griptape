from griptape.mixins.rule_mixin import RuleMixin
from griptape.rules import Rule, Ruleset
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
