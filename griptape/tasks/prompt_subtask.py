import logging

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.common import PromptStack
from griptape.configs import Defaults
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.tasks import PromptTask
from griptape.tasks.base_subtask import BaseSubtask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class PromptSubtask(BaseSubtask, FuturesExecutorMixin):
    _input: BaseArtifact = field(alias="input")

    @property
    def input(self) -> BaseArtifact:
        return self._input

    @property
    def prompt_stack(self) -> PromptStack:
        if isinstance(self.origin_task, PromptTask):
            return self.origin_task.prompt_stack
        else:
            raise Exception("PromptSubtask must be attached to a Task that implements PromptTask.")

    @property
    def prompt_driver(self) -> BasePromptDriver:
        if isinstance(self.origin_task, PromptTask):
            return self.origin_task.prompt_driver
        else:
            raise Exception("PromptSubtask must be attached to a Task that implements PromptTask.")

    def before_run(self) -> None:
        logger.info(
            "%s %s\nInput: %s\n",
            self.__class__.__name__,
            self.id,
            self.input,
        )

    def should_run(self) -> bool:
        return True

    def try_run(self) -> BaseArtifact:
        return self.prompt_driver.run(self.prompt_stack).to_artifact()

    def after_run(self) -> None:
        logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.to_text())

    def to_text(self) -> str:
        return self.output.to_text() if self.output is not None else ""

    def add_to_prompt_stack(self, prompt_driver: BasePromptDriver, prompt_stack: PromptStack) -> None:
        prompt_stack.add_assistant_message(self.input)
        if self.output is not None:
            prompt_stack.add_user_message(self.output.to_text())
