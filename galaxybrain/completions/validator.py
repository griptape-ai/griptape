from attrs import define
from typing import Optional
from galaxybrain.completions.completion_result import CompletionResult
from galaxybrain.rules.rule import Rule


@define()
class Validator():
    result: CompletionResult
    rules: list[Rule]
    rule_validations: dict[Rule, bool] = []

    def is_valid(self) -> Optional[bool]:
        if len(self.rules) == len(self.rule_validations):
            return all([validation[1] for validation in self.rule_validations])
        else:
            None

    def validate(self) -> bool:
        self.rule_validations = [(rule, rule.validator(self.result)) for rule in self.rules]

        return self.is_valid()

    def failed_rules(self) -> list[Rule]:
        return [validation[0].value for validation in self.rule_validations if not validation[1]]