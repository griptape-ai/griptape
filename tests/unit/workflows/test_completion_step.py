from galaxybrain.prompts import Prompt
from galaxybrain.workflows import CompletionStep, Workflow
from tests.mocks.mock_driver import MockCompletionDriver


class TestCompletionStep:
    def test_run(self):
        step = CompletionStep(input=Prompt("test"))
        workflow = Workflow(completion_driver=MockCompletionDriver())

        workflow.add_step(step)

        assert step.run().value == "mock output"
