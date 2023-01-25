from galaxybrain.prompts import Prompt
from galaxybrain.workflows import Workflow, CompletionStep
from galaxybrain.workflows.memory import BufferMemory
from tests.mocks.mock_driver import MockCompletionDriver


class TestBufferMemory:
    def test_after_run(self):
        memory = BufferMemory(buffer_size=2)

        workflow = Workflow(memory=memory, completion_driver=MockCompletionDriver())

        workflow.add_steps(
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test"))
        )

        workflow.start()

        assert len(workflow.memory.steps) == 2
