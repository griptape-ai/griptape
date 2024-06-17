from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from attrs import define, field, Factory
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
    output: Optional[BaseArtifact] = field(default=None, init=False)
    system_template_path: str = field(default="tasks/prompt_task/system.j2", kw_only=True)
    user_template_path: str = field(default="tasks/prompt_task/user.j2", kw_only=True)

    @property
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack()
        memory = self.structure.conversation_memory

        stack.add_system_input(self.generate_system_template())

        stack.add_user_input(self.input.to_text())

        if self.output:
            stack.add_assistant_input(self.output.to_text())

        if memory:
            # inserting at index 1 to place memory right after system prompt
            memory.add_to_prompt_stack(stack, 1)

        return stack

    @property
    def prompt_driver(self) -> BasePromptDriver:
        if self._prompt_driver is None:
            if self.structure is not None:
                self._prompt_driver = self.structure.config.prompt_driver
            else:
                raise ValueError("Prompt Driver is not set")
        return self._prompt_driver

    def preprocess(self, structure: Structure) -> PromptTask:
        super().preprocess(structure)
        if self.prompt_driver is not None:
            self.prompt_driver.structure = structure

        return self

    def generate_system_template(self) -> str:
        return self.render_system_template(rulesets=self.render_rulesets_template(rulesets=self.all_rulesets))

    def run(self) -> BaseArtifact:
        self.output = self.prompt_driver.run(self.prompt_stack)

        return self.output
