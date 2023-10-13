from abc import ABC
from typing import Any

from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseTextInputTask(BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    input_template: str = field(default=DEFAULT_INPUT_TEMPLATE)
    context: dict[str, Any] = field(factory=dict, kw_only=True)

    _input: TextArtifact = field(default=None, init=False)

    @property
    def input(self) -> TextArtifact:
        input_str = J2().render_from_string(self.input_template, **self.full_context)
            
        if self._input is not None:
            self._input.value = input_str
        else:
            self._input = TextArtifact(input_str)
            
        return self._input

    @property
    def full_context(self) -> dict[str, Any]:
        if self.structure:
            structure_context = self.structure.context(self)

            structure_context.update(self.context)

            return structure_context
        else:
            return {"args": [], **self.context}

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")
