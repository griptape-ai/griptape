from __future__ import annotations

import uuid

from attrs import Factory, define, field

from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.rules import BaseRule, Ruleset


@define(slots=False)
class RuleMixin(SerializableMixin):
    DEFAULT_RULESET_NAME = "Default Ruleset"

    _rulesets: list[Ruleset] = field(factory=list, kw_only=True, alias="rulesets", metadata={"serializable": True})
    rules: list[BaseRule] = field(factory=list, kw_only=True)
    _default_ruleset_name: str = field(default=Factory(lambda: RuleMixin.DEFAULT_RULESET_NAME), kw_only=True)
    _default_ruleset_id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)

    @property
    def rulesets(self) -> list[Ruleset]:
        rulesets = self._rulesets.copy()

        if self.rules:
            rulesets.append(Ruleset(id=self._default_ruleset_id, name=self._default_ruleset_name, rules=self.rules))

        return rulesets
