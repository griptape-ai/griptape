from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define

if TYPE_CHECKING:
    from galaxybrain.workflows.step_output import StepOutput
    from galaxybrain.rules.rule import Rule


@define()
class Validator:
    result: StepOutput
    rules: list[Rule] = []
    rule_validations: dict[Rule, bool] = {}

    def is_valid(self) -> Optional[bool]:
        if len(self.rules) == len(self.rule_validations):
            return all(self.rule_validations.values())
        else:
            return None

    def validate(self) -> bool:
        self.rule_validations = {rule: rule.validator(self.result) for rule in self.rules}

        return self.is_valid()

    def failed_rules(self) -> list[Rule]:
        return [rule for rule, is_valid in self.rule_validations.items() if not is_valid]
