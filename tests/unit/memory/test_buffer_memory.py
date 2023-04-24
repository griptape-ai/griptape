from griptape.tasks import PromptTask
from griptape.structures import Pipeline
from griptape.memory import BufferMemory
from tests.mocks.mock_driver import MockDriver


class TestBufferMemory:
    def test_after_run(self):
        memory = BufferMemory(buffer_size=2)

        pipeline = Pipeline(memory=memory, prompt_driver=MockDriver())

        pipeline.add_tasks(
            PromptTask("test"),
            PromptTask("test"),
            PromptTask("test"),
            PromptTask("test")
        )

        pipeline.run()
        pipeline.run()

        assert len(pipeline.memory.runs) == 2
