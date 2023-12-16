from __future__ import annotations
from abc import ABC
from typing import Any, Callable

from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.rules import Ruleset, Rule
from griptape.tasks import BaseTask
from griptape.tasks.base_ruleset_task import BaseRulesetTask
from griptape.utils import J2


@define
class BaseTextInputTask(BaseRulesetTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: str | TextArtifact | Callable[[BaseTask], TextArtifact] = field(default=DEFAULT_INPUT_TEMPLATE)
    context: dict[str, Any] = field(factory=dict, kw_only=True)

    @property
    def input(self) -> TextArtifact:
        if isinstance(self._input, TextArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    @input.setter
    def input(self, value: str | TextArtifact | Callable[[BaseTask], TextArtifact]) -> None:
        self._input = value

    @property
    def full_context(self) -> dict[str, Any]:
        if self.structure:
            structure_context = self.structure.context(self)

            structure_context.update(self.context)

            return structure_context
        else:
            return {}

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")
