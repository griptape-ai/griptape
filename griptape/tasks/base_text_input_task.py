from abc import ABC
from typing import Any

from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.rules import Ruleset, Rule
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseTextInputTask(BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"
    DEFAULT_RULESET_NAME = "Default Ruleset"
    ADDITIONAL_RULESET_NAME = "Additional Ruleset"

    input_template: str = field(default=DEFAULT_INPUT_TEMPLATE)
    context: dict[str, Any] = field(factory=dict, kw_only=True)
    rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)

    @property
    def input(self) -> TextArtifact:
        return TextArtifact(J2().render_from_string(self.input_template, **self.full_context))

    @property
    def full_context(self) -> dict[str, Any]:
        if self.structure:
            structure_context = self.structure.context(self)

            structure_context.update(self.context)

            return structure_context
        else:
            return {}

    @rulesets.validator
    def validate_rulesets(self, _, rulesets: list[Ruleset]) -> None:
        if not rulesets:
            return

        if self.rules:
            raise ValueError("Can't have both rulesets and rules specified.")

    @rules.validator
    def validate_rules(self, _, rules: list[Rule]) -> None:
        if not rules:
            return

        if self.rulesets:
            raise ValueError("Can't have both rules and rulesets specified.")

    @property
    def all_rulesets(self) -> list[Ruleset]:
        structure_rulesets = []

        if self.structure:
            if self.structure.rulesets:
                structure_rulesets = self.structure.rulesets
            elif self.structure.rules:
                structure_rulesets = [Ruleset(name=self.DEFAULT_RULESET_NAME, rules=self.structure.rules)]

        task_rulesets = []
        if self.rulesets:
            task_rulesets = self.rulesets
        elif self.rules:
            if structure_rulesets:
                task_ruleset_name = self.ADDITIONAL_RULESET_NAME
            else:
                task_ruleset_name = self.DEFAULT_RULESET_NAME

            task_rulesets = [Ruleset(name=task_ruleset_name, rules=self.rules)]

        return structure_rulesets + task_rulesets

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")
