from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.prompts import Prompt
from galaxybrain.workflows import Step
from galaxybrain.workflows.step_output import StepOutput

if TYPE_CHECKING:
    from galaxybrain.drivers import Driver


@define
class CompletionStep(Step):
    driver: Optional[Driver] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        if self.driver is None:
            active_driver = self.workflow.driver
        else:
            active_driver = self.driver

        self.output = active_driver.run(value=self.to_string())

        return self.output

    def to_string(self) -> str:
        question = Prompt.j2().get_template("input.j2").render(question=self.input.value)

        if self.workflow:
            intro = Prompt.intro(self.workflow.rules)
            conversation = Prompt.conversation(self.workflow)

            if self.output:
                return f"{intro}\n{conversation}"
            else:
                return f"{intro}\n{conversation}\n{question}"
        else:
            return question
