from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from attr import define, field, Factory
from griptape.utils import PromptStack
from griptape.utils import J2
from griptape.tasks import BaseTextInputTask
from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.structures import Structure


@define
class PromptTask(BaseTextInputTask):
    _prompt_driver: Optional[BasePromptDriver] = field(default=None, kw_only=True, alias="prompt_driver")
    generate_system_template: Callable[[PromptTask], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True), kw_only=True
    )

    output: Optional[BaseArtifact] = field(default=None, init=False)

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

    @property
    def prompt_driver(self) -> BasePromptDriver:
        if self._prompt_driver is None:
            if self.structure is not None:
                self._prompt_driver = self.structure.config.global_drivers.prompt_driver
            else:
                raise ValueError("Prompt Driver is not set")
        return self._prompt_driver

    def preprocess(self, structure: Structure) -> PromptTask:
        super().preprocess(structure)
        if self.prompt_driver is not None:
            self.prompt_driver.structure = structure

        return self

    def default_system_template_generator(self, _: PromptTask) -> str:
        return J2("tasks/prompt_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets)
        )

    def run(self) -> BaseArtifact:
        self.output = self.prompt_driver.run(self.prompt_stack)

        return self.output
