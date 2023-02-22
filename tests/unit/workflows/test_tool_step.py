from galaxybrain.prompts import Prompt
from galaxybrain.workflows import Workflow, ToolStep
from tests.mocks.mock_driver import MockCompletionDriver


class TestComputeStep:
    def test_run(self):
        step = ToolStep(input=Prompt("test"))
        workflow = Workflow(completion_driver=MockCompletionDriver())

        workflow.add_step(step)

        assert step.run().value == "mock output"
