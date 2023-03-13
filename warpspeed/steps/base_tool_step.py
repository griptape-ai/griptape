from __future__ import annotations
import ast
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from warpspeed.tools import Tool
from warpspeed.utils import J2
from warpspeed.steps import PromptStep
from warpspeed.artifacts import TextOutput

if TYPE_CHECKING:
    from warpspeed.steps import ToolSubstep


@define
class BaseToolStep(PromptStep, ABC):
    JSON_PARSE_ERROR_MSG = f"invalid input, try again"

    substeps: list[ToolSubstep] = field(factory=list, kw_only=True)

    def run(self) -> TextOutput:
        from warpspeed.steps import ToolSubstep

        action_output = self.active_driver().run(value=self.structure.to_prompt_string(self))
        action_name, action_input = self.parse_tool_action(action_output.value)

        while True:
            substep = self.add_substep(
                ToolSubstep(
                    action_output.value,
                    tool_step=self,
                    action_name=action_name,
                    action_input=action_input
                )
            )

            substep.before_run()
            substep.run()
            substep.after_run()

            if substep.action_name == "exit":
                action_output = self.active_driver().run(value=self.structure.to_prompt_string(self))
                substep.is_exiting = False
                break
            else:
                action_output = self.active_driver().run(value=self.structure.to_prompt_string(self))
                action_name, action_input = self.parse_tool_action(action_output.value)

        self.output = action_output

        return self.output

    def render(self) -> str:
        return J2("prompts/steps/tool/tool.j2").render(
            step=self
        )

    def find_substep(self, step_id: str) -> Optional[ToolSubstep]:
        return next((step for step in self.substeps if step.id == step_id), None)

    def add_substep(self, substep: ToolSubstep) -> ToolSubstep:
        substep.structure = self.structure

        if len(self.substeps) > 0:
            self.substeps[-1].add_child(substep)

        self.substeps.append(substep)

        return substep

    def parse_tool_action(self, value: str) -> (str, str):
        try:
            pattern = r"^Action:\s*(.*)$"
            matches = re.findall(pattern, value, re.MULTILINE)

            if len(matches) > 0:
                parsed_value = ast.literal_eval(matches[-1])

                return parsed_value.get("tool"), parsed_value.get("input")
            else:
                return "error", f"error: {self.JSON_PARSE_ERROR_MSG}"

        except Exception as e:
            self.structure.logger.error(f"Step {self.id}\nError parsing tool action: {e}")

            return "error", f"error: {self.JSON_PARSE_ERROR_MSG}"

    @abstractmethod
    def find_tool(self, action_name: str) -> Optional[Tool]:
        ...
