from galaxybrain.workflows import Workflow, PromptStep
from galaxybrain.workflows.memory import BufferMemory
from tests.mocks.mock_driver import MockDriver


class TestBufferMemory:
    def test_after_run(self):
        memory = BufferMemory(buffer_size=2)

        workflow = Workflow(memory=memory, prompt_driver=MockDriver())

        workflow.add_steps(
            PromptStep("test"),
            PromptStep("test"),
            PromptStep("test"),
            PromptStep("test")
        )

        workflow.start()

        assert len(workflow.memory.steps) == 2
