from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows import Step
from galaxybrain.workflows.step_output import StepOutput

if TYPE_CHECKING:
    from galaxybrain.drivers import CompletionDriver


@define
class CompletionStep(Step):
    driver: Optional[CompletionDriver] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        self.output = self.active_driver().run(value=self.workflow.to_prompt_string())

        return self.output

    def active_driver(self) -> CompletionDriver:
        if self.driver is None:
            return self.workflow.completion_driver
        else:
            return self.driver

    def render(self) -> str:
        return J2("steps/completion.j2").render(
            step=self
        )
