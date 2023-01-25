from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.workflows import Step
from galaxybrain.workflows.step_output import StepOutput

if TYPE_CHECKING:
    from galaxybrain.drivers import CompletionDriver


@define
class CompletionStep(Step):
    driver: Optional[CompletionDriver] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        if self.driver is None:
            active_driver = self.workflow.completion_driver
        else:
            active_driver = self.driver

        self.output = active_driver.run(value=self.workflow.to_prompt_string())

        return self.output

