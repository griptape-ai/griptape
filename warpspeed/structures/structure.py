from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Optional, Union, TYPE_CHECKING
from attrs import define, field
from warpspeed.drivers import PromptDriver, OpenAiPromptDriver
from warpspeed.utils import J2

if TYPE_CHECKING:
    from warpspeed.rules import Rule
    from warpspeed.steps import Step


@define
class Structure(ABC):
    prompt_driver: PromptDriver = field(default=OpenAiPromptDriver(), kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    steps: list[Step] = field(factory=list, kw_only=True)

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

    def before_run(self, step: Step) -> None:
        pass

    def after_run(self, step: Step) -> None:
        pass

    @abstractmethod
    def add_step(self, step: Step) -> Step:
        ...

    @abstractmethod
    def run(self) -> Union[Step, list[Step]]:
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
