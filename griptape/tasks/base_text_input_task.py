from abc import ABC
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseTextInputTask(BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    input_template: str = field(default=DEFAULT_INPUT_TEMPLATE)
    context: dict[str, any] = field(factory=dict, kw_only=True)

    @property
    def input(self) -> TextArtifact:
        return TextArtifact(
            J2().render_from_string(
                self.input_template,
                **self.full_context
            )
        )

    @property
    def full_context(self) -> dict[str, any]:
        if self.structure:
            structure_context = self.structure.context(self)

            structure_context.update(self.context)

            return structure_context
        else:
            return {}
