from galaxybrain.prompts import Prompt
from galaxybrain.workflows import Workflow, ComputeStep
from tests.mocks.mock_driver import MockCompletionDriver


class TestComputeStep:
    def test_run(self):
        step = ComputeStep(input=Prompt("test"))
        workflow = Workflow(completion_driver=MockCompletionDriver())

        workflow.add_step(step)

        assert step.run().value == "mock output"

    def test_run_code(self):
        assert ComputeStep(input=Prompt("test")).run_code("""print(math.sqrt(9))""") == "3.0"
        assert ComputeStep(input=Prompt("test")).run_code("""print(np.array([1, 2, 3]))""") == "[1 2 3]"
