from __future__ import annotations
import json
import logging
import uuid
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, Union, TYPE_CHECKING
from attrs import define, field, Factory
from rich.logging import RichHandler
from warpspeed.drivers import PromptDriver, OpenAiPromptDriver
from warpspeed.utils import J2

if TYPE_CHECKING:
    from warpspeed.rules import Rule
    from warpspeed.steps import Step


@define
class Structure(ABC):
    LOGGER_NAME = "warpspeed"

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    prompt_driver: PromptDriver = field(default=OpenAiPromptDriver(), kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    steps: list[Step] = field(factory=list, kw_only=True)
    custom_logger: Optional[Logger] = field(default=None, kw_only=True)

    _execution_args: tuple = ()
    _logger: Optional[Logger] = None

    def __attrs_post_init__(self):
        for step in self.steps:
            step.structure = self

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

                self._logger.handlers = [
                    RichHandler(
                        show_time=True,
                        show_path=False
                    )
                ]

            return self._logger

    def is_finished(self) -> bool:
        return all(s.is_finished() for s in self.steps)

    def is_executing(self) -> bool:
        return any(s for s in self.steps if s.is_executing())

    def is_empty(self) -> bool:
        return not self.steps

    def find_step(self, step_id: str) -> Optional[Step]:
        return next((step for step in self.steps if step.id == step_id), None)

    def add_steps(self, *steps: Step) -> list[Step]:
        return [self.add_step(s) for s in steps]

    def prompt_stack(self, step: Step) -> list[str]:
        from warpspeed.steps import ToolStep, ToolkitStep

        if isinstance(step, ToolStep):
            tools = [step.tool]
        elif isinstance(step, ToolkitStep):
            tools = step.tools
        else:
            tools = []

        stack = [
            J2("prompts/context.j2").render(
                rules=self.rules,
                tool_names=str.join(", ", [tool.name for tool in tools]),
                tools=[J2("prompts/tool.j2").render(tool=tool) for tool in tools]
            )
        ]

        return stack

    def to_prompt_string(self, step: Step) -> str:
        return str.join("\n", self.prompt_stack(step))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def context(self, step: Step) -> dict[str, any]:
        return {
            "args": self.execution_args,
            "structure": self,
        }

    @abstractmethod
    def add_step(self, step: Step) -> Step:
        ...

    @abstractmethod
    def run(self, *args) -> Union[Step, list[Step]]:
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, workflow_dict: dict) -> Structure:
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, workflow_json: str) -> Structure:
        ...
