from __future__ import annotations

from typing import Optional

from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows import Step
from galaxybrain.workflows.step_output import StepOutput


@define
class ToolSubstep(Step):
    action_name: Optional[str] = field(default=None, kw_only=True)
    action_param: Optional[str] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        tool = self.workflow.tools.get(self.action_name)

        if tool:
            observation = tool.run(self.action_param)
        else:
            observation = "Tool not found"

        self.output = StepOutput(observation)

        return self.output

    def render(self) -> str:
        return J2("steps/tool/substep.j2").render(
            step=self
        )
