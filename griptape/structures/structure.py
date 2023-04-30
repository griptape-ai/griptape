from __future__ import annotations
import json
import logging
import uuid
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, Union, TYPE_CHECKING
from attr import define, field, Factory
from rich.logging import RichHandler
from griptape.tasks import ActionSubtask
from griptape import utils
from griptape.drivers import BasePromptDriver, OpenAiPromptDriver
from griptape.utils import J2
from griptape.core import ToolLoader

if TYPE_CHECKING:
    from griptape.rules import Rule
    from griptape.tasks import BaseTask


@define
class Structure(ABC):
    LOGGER_NAME = "griptape-flow"

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    prompt_driver: BasePromptDriver = field(default=OpenAiPromptDriver(), kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    tasks: list[BaseTask] = field(factory=list, kw_only=True)
    custom_logger: Optional[Logger] = field(default=None, kw_only=True)
    logger_level: int = field(default=logging.INFO, kw_only=True)
    tool_loader: ToolLoader = field(default=ToolLoader(), kw_only=True)
    _execution_args: tuple = ()
    _logger: Optional[Logger] = None

    def __attrs_post_init__(self):
        for task in self.tasks:
            task.structure = self

    @property
    def execution_args(self) -> tuple:
        return self._execution_args

    @property
    def logger(self) -> Logger:
        if self.custom_logger:
            return self.custom_logger
        else:
            if self._logger is None:
                self._logger = logging.getLogger(self.LOGGER_NAME)

                self._logger.propagate = False
                self._logger.level = self.logger_level

                self._logger.handlers = [
                    RichHandler(
                        show_time=True,
                        show_path=False
                    )
                ]

            return self._logger

    def is_finished(self) -> bool:
        return all(s.is_finished() for s in self.tasks)

    def is_executing(self) -> bool:
        return any(s for s in self.tasks if s.is_executing())

    def find_task(self, task_id: str) -> Optional[BaseTask]:
        return next((task for task in self.tasks if task.id == task_id), None)

    def add_tasks(self, *tasks: BaseTask) -> list[BaseTask]:
        return [self.add_task(s) for s in tasks]

    def prompt_stack(self, task: BaseTask) -> list[str]:
        from griptape.tasks import ToolkitTask

        tools = task.tools if isinstance(task, ToolkitTask) else []
        ramps = [r for r in task.ramps if len(r.activities()) > 0] if isinstance(task, ToolkitTask) else []
        action_schema = utils.minify_json(
            json.dumps(
                ActionSubtask.ACTION_SCHEMA.json_schema("ActionSchema")
            )
        )

        stack = [
            J2("prompts/base.j2").render(
                rules=self.rules,
                action_schema=action_schema,
                ramp_names=str.join(", ", [ramp.name for ramp in ramps]),
                ramps=[J2("prompts/ramp.j2").render(ramp=ramp) for ramp in ramps],
                tool_names=str.join(", ", [tool.name for tool in tools]),
                tools=[J2("prompts/tool.j2").render(tool=tool) for tool in tools]
            )
        ]

        return stack

    def to_prompt_string(self, task: BaseTask) -> str:
        return self.stack_to_prompt_string(self.prompt_stack(task))

    def stack_to_prompt_string(self, stack: list[str]) -> str:
        return str.join("\n", stack)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def context(self, task: BaseTask) -> dict[str, any]:
        return {
            "args": self.execution_args,
            "structure": self,
        }

    @abstractmethod
    def add_task(self, task: BaseTask) -> BaseTask:
        ...

    @abstractmethod
    def run(self, *args) -> Union[BaseTask, list[BaseTask]]:
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, structure_dict: dict) -> Structure:
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, structure_json: str) -> Structure:
        ...
