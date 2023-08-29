from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestPromptSubtask:
    def test_run(self):
        task = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_to_text(self):
        task = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(task)

        assert task.input.to_text() == "test value"
