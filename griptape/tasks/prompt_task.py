from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact
from griptape.common import MessageStack
from griptape.tasks import BaseTask
from griptape.utils import J2
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.mixins import RuleMixin

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.structures import Structure


@define
class PromptTask(RuleMixin, BaseTask):
    _prompt_driver: Optional[BasePromptDriver] = field(default=None, kw_only=True, alias="prompt_driver")
    generate_system_template: Callable[[PromptTask], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True), kw_only=True
    )
    _input: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
        alias="input",
    )

    @property
    def input(self) -> BaseArtifact:
        return self._process_task_input(self._input)

    @input.setter
    def input(self, value: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact]) -> None:
        self._input = value

    output: Optional[BaseArtifact] = field(default=None, init=False)

    @property
    def message_stack(self) -> MessageStack:
        stack = MessageStack()
        memory = self.structure.conversation_memory

        stack.add_system_message(self.generate_system_template(self))

        stack.add_user_message(self.input)

        if self.output:
            stack.add_assistant_message(self.output)

        if memory:
            # inserting at index 1 to place memory right after system prompt
            memory.add_to_message_stack(stack, 1)

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

    def default_system_template_generator(self, _: PromptTask) -> str:
        return J2("tasks/prompt_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets)
        )

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")

    def run(self) -> BaseArtifact:
        self.output = self.prompt_driver.run(self.message_stack)

        return self.output

    def _process_task_input(
        self, task_input: str | tuple | list | BaseArtifact | Callable[[BaseTask], BaseArtifact]
    ) -> BaseArtifact:
        if isinstance(task_input, TextArtifact):
            task_input.value = J2().render_from_string(task_input.value, **self.full_context)

            return task_input
        elif isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        elif isinstance(task_input, str):
            return self._process_task_input(TextArtifact(task_input))
        elif isinstance(task_input, BaseArtifact):
            return task_input
        elif isinstance(task_input, list) or isinstance(task_input, tuple):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        else:
            raise ValueError(f"Invalid input type: {type(task_input)} ")
