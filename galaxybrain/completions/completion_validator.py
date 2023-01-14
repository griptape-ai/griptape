from attrs import define
from typing import Optional
from galaxybrain.prompts.prompt_rule import PromptRule


@define()
class CompletionValidator():
    result: str
    rules: list[PromptRule]
    rule_validations: dict[PromptRule, bool] = []

    def is_valid(self) -> Optional[bool]:
        if len(self.rules) == len(self.rule_validations):
            return all([validation[0] for validation in self.rule_validations])
        else:
            None

    def validate(self) -> None:
        self.rule_validations = [(rule, rule.validator(self.result)) for rule in self.rules]

    def failed_rules(self) -> list[PromptRule]:
        return [validation[0].value for validation in self.rule_validations if not validation[1]]