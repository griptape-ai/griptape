from warpspeed.steps import PromptStep
from warpspeed.structures import Pipeline
from warpspeed.memory import BufferMemory
from tests.mocks.mock_driver import MockDriver


class TestBufferMemory:
    def test_after_run(self):
        memory = BufferMemory(buffer_size=2)

        pipeline = Pipeline(memory=memory, prompt_driver=MockDriver())

        pipeline.add_steps(
            PromptStep("test"),
            PromptStep("test"),
            PromptStep("test"),
            PromptStep("test")
        )

        pipeline.run()

        assert len(pipeline.memory.steps) == 2
