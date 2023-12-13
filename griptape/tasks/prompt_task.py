from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from attr import define, field, Factory
from griptape.utils import PromptStack
from griptape.utils import J2
from griptape.tasks import BaseTextInputTask
from griptape.artifacts import TextArtifact, InfoArtifact, ErrorArtifact

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define
class PromptTask(BaseTextInputTask):
    prompt_driver: BasePromptDriver | None = field(default=None, kw_only=True)
    generate_system_template: Callable[[PromptTask], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True), kw_only=True
    )

    output: TextArtifact | ErrorArtifact | InfoArtifact | None = field(default=None, init=False)

    @property
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack()
        memory = self.structure.conversation_memory

        stack.add_system_input(self.generate_system_template(self))

        stack.add_user_input(self.input.to_text())

        if self.output:
            stack.add_assistant_input(self.output.to_text())

        if memory:
            # inserting at index 1 to place memory right after system prompt
            stack.add_conversation_memory(memory, 1)

        return stack

    def default_system_template_generator(self, _: PromptTask) -> str:
        return J2("tasks/prompt_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets)
        )

    def run(self) -> TextArtifact:
        self.output = self.active_driver().run(self.prompt_stack)

        return self.output

    def active_driver(self) -> BasePromptDriver:
        if self.prompt_driver is None:
            return self.structure.prompt_driver
        else:
            return self.prompt_driver
