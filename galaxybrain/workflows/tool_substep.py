from __future__ import annotations
from typing import Optional
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows import PromptStep, BaseToolStep
from galaxybrain.artifacts import StepOutput


@define
class ToolSubstep(PromptStep):
    tool_step: BaseToolStep = field(kw_only=True)
    action_name: Optional[str] = field(default=None, kw_only=True)
    action_input: Optional[str] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        if self.action_name == "exit":
            self.output = StepOutput(None)
        elif self.action_name == "error":
            self.output = StepOutput(self.action_input)
        else:

            tool = self.tool_step.find_tool(self.action_name)

            if tool:
                observation = tool.run(self.action_input)
            else:
                observation = "tool not found"

            self.output = StepOutput(observation)

        return self.output

    def render(self) -> str:
        return J2("prompts/steps/tool/substep.j2").render(
            step=self
        )
