from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact
from griptape.common import PromptStack
from griptape.mixins import RuleMixin
from griptape.tasks import BaseTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define
class PromptTask(RuleMixin, BaseTask):
    _prompt_driver: Optional[BasePromptDriver] = field(default=None, kw_only=True, alias="prompt_driver")
    generate_system_template: Callable[[PromptTask], str] = field(
        default=Factory(lambda self: self.default_system_template_generator, takes_self=True),
        kw_only=True,
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
    def prompt_stack(self) -> PromptStack:
        stack = PromptStack()
        memory = self.structure.conversation_memory

        system_template = self.generate_system_template(self)
        if system_template:
            stack.add_system_message(system_template)

        stack.add_user_message(self.input)

        if self.output:
            stack.add_assistant_message(self.output)

        if memory is not None:
            # insert memory into the stack right before the user messages
            memory.add_to_prompt_stack(stack, 1 if system_template else 0)

        return stack

    @property
    def prompt_driver(self) -> BasePromptDriver:
        if self._prompt_driver is None:
            if self.structure is not None:
                self._prompt_driver = self.structure.config.prompt_driver
            else:
                raise ValueError("Prompt Driver is not set")
        return self._prompt_driver

    def default_system_template_generator(self, _: PromptTask) -> str:
        return J2("tasks/prompt_task/system.j2").render(
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=self.all_rulesets),
        )

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.output.to_text())

    def run(self) -> BaseArtifact:
        message = self.prompt_driver.run(self.prompt_stack)

        return message.to_artifact()

    def _process_task_input(
        self,
        task_input: str | tuple | list | BaseArtifact | Callable[[BaseTask], BaseArtifact],
    ) -> BaseArtifact:
        if isinstance(task_input, TextArtifact):
            task_input.value = J2().render_from_string(task_input.value, **self.full_context)

            return task_input
        elif isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        elif isinstance(task_input, ListArtifact):
            return ListArtifact([self._process_task_input(elem) for elem in task_input.value])
        elif isinstance(task_input, BaseArtifact):
            return task_input
        elif isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        else:
            return self._process_task_input(TextArtifact(task_input))
