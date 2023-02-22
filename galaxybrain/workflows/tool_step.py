from __future__ import annotations
from attrs import define
from galaxybrain.utils import J2
from galaxybrain.workflows import CompletionStep, ToolActionStep
from galaxybrain.workflows.step_output import StepOutput


@define
class ToolStep(CompletionStep):
    def run(self) -> StepOutput:
        from galaxybrain.prompts import Prompt

        self.output = self.active_driver().run(value=self.workflow.to_prompt_string())

        self.workflow.add_step_after(self, ToolActionStep(
            input=Prompt(self.output.value)
        ))

        return self.output

    def render(self) -> str:
        return J2("steps/tool/start.j2").render(
            step=self
        )
