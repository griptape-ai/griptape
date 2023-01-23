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

        self.output = active_driver.run(value=self.to_string())

        return self.output

    def to_string(self) -> str:
        question = self.input.j2().get_template("input.j2").render(question=self.input.value)

        if self.workflow:
            intro = self.input.intro(self.workflow.rules)
            conversation = self.input.conversation(self.workflow)

            if self.output:
                return f"{intro}\n{conversation}"
            else:
                return f"{intro}\n{conversation}\n{question}"
        else:
            return question
