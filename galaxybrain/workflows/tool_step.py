from __future__ import annotations
import re
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows import CompletionStep, ToolSubstep
from galaxybrain.workflows.memory import Memory
from galaxybrain.workflows.step_output import StepOutput


@define
class ToolStep(CompletionStep):
    substeps: list[ToolSubstep] = field(factory=list, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)

    def run(self) -> StepOutput:
        from galaxybrain.prompts import Prompt

        temp_output = self.active_driver().run(value=self.workflow.to_prompt_string())
        action_name, action_param = self.__extract_action_and_param(temp_output.value)

        while action_name != "exit" and action_name is not None:
            substep = self.add_substep(
                ToolSubstep(
                    Prompt(temp_output.value),
                    action_name=action_name,
                    action_param=action_param
                )
            )

            substep.run()

            temp_output = self.active_driver().run(value=self.workflow.to_prompt_string())
            action_name, action_param = self.__extract_action_and_param(temp_output.value)

        self.output = StepOutput(action_param)

        return self.output

    def render(self) -> str:
        return J2("steps/tool/tool.j2").render(
            step=self
        )

    def add_substep(self, substep: ToolSubstep) -> ToolSubstep:
        substep.workflow = self.workflow

        if len(self.substeps) > 0:
            self.substeps[-1].add_child(substep)

        self.substeps.append(substep)

        return substep

    def __extract_action_and_param(self, value: str) -> (str, str):
        pattern = r'(\w+)\((.*?)\)(?!.*\()(?=$)'

        try:
            match = re.search(pattern, value, re.DOTALL)

            if match:
                tool_name = match.group(1)
                content = match.group(2)

                return tool_name, content
            else:
                return None, None
        except Exception as e:
            return None, None
