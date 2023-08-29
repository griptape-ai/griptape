from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestPromptSubtask:
    def test_run(self):
        subtask = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(subtask)

        assert subtask.run().to_text() == "mock output"

    def test_to_text(self):
        subtask = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(subtask)

        assert subtask.input.to_text() == "test value"
