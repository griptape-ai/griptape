from __future__ import annotations
import json
import re
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows import PromptStep, ToolSubstep
from galaxybrain.workflows.memory import Memory
from galaxybrain.workflows.step_output import StepOutput


@define
class ToolStep(PromptStep):
    JSON_PARSE_ERROR_MSG = f"invalid JSON, try again"

    substeps: list[ToolSubstep] = field(factory=list, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)

    def run(self) -> StepOutput:
        temp_output = self.active_driver().run(value=self.workflow.to_prompt_string())
        action_name, action_input = self.parse_tool_action(temp_output.value)

        while action_name is not None:
            substep = self.add_substep(
                ToolSubstep(
                    temp_output.value,
                    action_name=action_name,
                    action_input=action_input
                )
            )

            substep.run()

            if substep.action_name == "exit":
                break
            else:
                temp_output = self.active_driver().run(value=self.workflow.to_prompt_string())
                action_name, action_input = self.parse_tool_action(temp_output.value)

        if action_input is None:
            final_output = temp_output.value
        else:
            final_output = action_input

        self.output = StepOutput(final_output)

        return self.output

    def render(self) -> str:
        return J2("prompts/steps/tool/tool.j2").render(
            step=self
        )

    def add_substep(self, substep: ToolSubstep) -> ToolSubstep:
        substep.workflow = self.workflow

        if len(self.substeps) > 0:
            self.substeps[-1].add_child(substep)

        self.substeps.append(substep)

        return substep

    def parse_tool_action(self, value: str) -> (str, str):
        try:
            pattern = r"^Action:\s*(.*)$"

            matches = re.findall(pattern, value, re.MULTILINE)

            if len(matches) > 0:
                parsed_value = json.loads(matches[-1])

                return parsed_value.get("tool"), parsed_value.get("input")
            else:
                return "error", self.JSON_PARSE_ERROR_MSG
        except Exception as e:
            return "error", self.JSON_PARSE_ERROR_MSG
