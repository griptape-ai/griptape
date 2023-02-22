from __future__ import annotations
import re
from typing import Optional
from attr import field
from attrs import define
from galaxybrain.utils import J2
from galaxybrain.workflows import CompletionStep, StepOutput


@define
class ToolActionStep(CompletionStep):
    action_name: Optional[str] = field(default=None, kw_only=True)
    action_param: Optional[str] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        from galaxybrain.prompts import Prompt

        self.action_name, self.action_param = self.extract_action_and_param()

        if self.action_name == "exit":
            self.output = StepOutput(self.action_param)
        else:
            self.output = self.active_driver().run(value=self.workflow.to_prompt_string())

            self.workflow.add_step_after(self, ToolActionStep(
                input=Prompt(self.output.value)
            ))

        return self.output

    def render(self) -> str:
        if self.action_name == "exit":
            return J2("steps/tool/stop.j2").render(
                result=self.action_param
            )
        else:
            tool = self.workflow.find_tool(self.action_name)

            if tool:
                observation = tool.run(self.action_param)
            else:
                observation = "Tool not found"

            return J2("steps/tool/observation.j2").render(
                step=self,
                observation=observation
            )

    def extract_action_and_param(self) -> (str, str):
        pattern = r'(\w+)\((.*?)\)(?!.*\()(?=$)'

        try:
            match = re.search(pattern, self.input.value, re.DOTALL)

            if match:
                tool_name = match.group(1)
                content = match.group(2)

                return tool_name, content
            else:
                return None, None
        except Exception as e:
            return None, None
