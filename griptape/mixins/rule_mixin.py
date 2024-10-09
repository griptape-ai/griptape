from __future__ import annotations

from attrs import define, field

from griptape.rules import BaseRule, Ruleset


@define(slots=False)
class RuleMixin:
    DEFAULT_RULESET_NAME = "Default Ruleset"

    _rulesets: list[Ruleset] = field(factory=list, kw_only=True, alias="rulesets")
    rules: list[BaseRule] = field(factory=list, kw_only=True)

    @property
    def rulesets(self) -> list[Ruleset]:
        rulesets = self._rulesets

        if self.rules:
            rulesets.append(Ruleset(name=self.DEFAULT_RULESET_NAME, rules=self.rules))

        return rulesets
