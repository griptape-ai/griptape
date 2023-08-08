from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, Union
from attr import define, field, Factory
from griptape.core import PromptStack
from griptape.utils import J2
from griptape.tasks import BaseTask
from griptape.artifacts import TextArtifact, InfoArtifact, ErrorArtifact

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define
class PromptTask(BaseTask):
    DEFAULT_PROMPT_TEMPLATE = "{{ args[0] }}"

    prompt_template: str = field(default=DEFAULT_PROMPT_TEMPLATE)
    context: dict[str, any] = field(factory=dict, kw_only=True)
    prompt_driver: Optional[BasePromptDriver] = field(default=None, kw_only=True)
    system_template_generator: Callable[[], str] = field(
        default=Factory(
            lambda self: self.default_system_template_generator,
            takes_self=True
        ),
        kw_only=True
    )

    output: Optional[Union[TextArtifact, ErrorArtifact, InfoArtifact]] = field(default=None, init=False)

    @property
    def default_system_template_generator(self) -> Callable[[], str]:
        return lambda: J2("tasks/prompt_task/system.j2").render(
            rulesets=self.structure.rulesets
        )

    @property
    def input(self) -> TextArtifact:
        return TextArtifact(
            J2().render_from_string(
                self.prompt_template,
                **self.full_context
            )
        )

    @property
    def full_context(self) -> dict[str, any]:
        structure_context = self.structure.context(self)

        structure_context.update(self.context)

        return structure_context

    @property
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack()
        memory = self.structure.memory

        stack.add_system_input(
            self.system_template_generator()
        )

        if memory:
            for r in memory.runs:
                stack.add_user_input(r.input)
                stack.add_assistant_input(r.output)

        stack.add_user_input(self.input.to_text())

        if self.output:
            stack.add_assistant_input(self.output.to_text())

        return stack

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"Task {self.id}\nInput: {self.input.to_text()}")

    def run(self) -> TextArtifact:
        self.output = self.active_driver().run(self.prompt_stack)

        return self.output

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"Task {self.id}\nOutput: {self.output.to_text()}")

    def active_driver(self) -> BasePromptDriver:
        if self.prompt_driver is None:
            return self.structure.prompt_driver
        else:
            return self.prompt_driver
