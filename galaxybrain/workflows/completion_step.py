from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.workflows import Step, Workflow
from galaxybrain.workflows.step_output import StepOutput

if TYPE_CHECKING:
    from galaxybrain.drivers import Driver


@define
class CompletionStep(Step):
    driver: Optional[Driver] = field(default=None, kw_only=True)

    def run(self, workflow: Workflow) -> StepOutput:
        prompt_value = self.input.to_string(workflow=workflow)

        if self.driver is None:
            active_driver = workflow.driver
        else:
            active_driver = self.driver

        self.output = active_driver.run(value=prompt_value)

        return self.output
