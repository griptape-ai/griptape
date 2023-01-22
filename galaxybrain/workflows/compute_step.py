from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import sys
import importlib
from io import StringIO
from attrs import define, field
from galaxybrain.prompts import Prompt
from galaxybrain.workflows import CompletionStep
from galaxybrain.workflows.step_output import StepOutput

if TYPE_CHECKING:
    from galaxybrain.drivers import Driver


@define
class ComputeStep(CompletionStep):
    AVAILABLE_LIBRARIES = {"numpy": "np", "math": "math"}

    driver: Optional[Driver] = field(default=None, kw_only=True)

    def run(self) -> StepOutput:
        if self.driver is None:
            active_driver = self.workflow.driver
        else:
            active_driver = self.driver

        self.input.value = self.input.j2().get_template("compute_question.j2").render(
            libraries=str.join(", ", self.AVAILABLE_LIBRARIES.values()),
            question=self.input.value
        )

        self.output = active_driver.run(value=self.to_string())

        followup_question = self.input.j2().get_template("compute_followup_question.j2").render(
            question=self.__run_code(self.output.value)
        )

        self.workflow.add_step_after(self, CompletionStep(input=Prompt(followup_question)))

        return self.output

    def __run_code(self, code: str) -> str:
        global_stdout = sys.stdout
        sys.stdout = local_stdout = StringIO()

        try:
            for lib, alias in self.AVAILABLE_LIBRARIES.items():
                imported_lib = importlib.import_module(lib)
                globals()[alias] = imported_lib

            exec(code, {}, {alias: eval(alias) for alias in self.AVAILABLE_LIBRARIES.values()})

            sys.stdout = global_stdout
            output = local_stdout.getvalue()
        except Exception as e:
            sys.stdout = global_stdout
            output = str(e)
        return output
