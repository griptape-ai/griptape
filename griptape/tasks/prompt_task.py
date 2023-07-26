from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from attr import define, field, Factory
from griptape.utils import J2
from griptape.tasks import BaseTask
from griptape.artifacts import TextArtifact, BaseArtifact

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define
class PromptTask(BaseTask):
    DEFAULT_PROMPT_TEMPLATE = "{{ args[0] }}"

    prompt_template: str = field(default=DEFAULT_PROMPT_TEMPLATE)
    context: dict[str, any] = field(factory=dict, kw_only=True)
    driver: Optional[BasePromptDriver] = field(default=None, kw_only=True)
    render_system_prompt: Callable[[], str] = field(
        default=Factory(lambda self: self.default_system_prompt, takes_self=True),
        kw_only=True
    )

    output: Optional[BaseArtifact] = field(default=None, init=False)

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

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"Task {self.id}\nInput: {self.input.to_text()}")

    def run(self) -> TextArtifact:
        self.output = self.active_driver().run(value=self.structure.to_prompt_string(self))

        return self.output

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"Task {self.id}\nOutput: {self.output.to_text()}")

    def active_driver(self) -> BasePromptDriver:
        if self.driver is None:
            return self.structure.prompt_driver
        else:
            return self.driver

    def render(self) -> str:
        return J2("prompts/tasks/prompt/conversation.j2").render(
            task=self
        )

    def default_system_prompt(self) -> str:
        return J2("tasks/prompt_task/system.j2").render(
            rulesets=self.structure.rulesets,
        )
