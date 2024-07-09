import pytest
from tests.mocks.mock_structure_config import MockStructureConfig
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestPromptTask:
    def test_run(self):
        task = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_to_text(self):
        task = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(task)

        assert task.input.to_text() == "test value"

    def test_config_prompt_driver(self):
        task = PromptTask("test")
        Pipeline(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.prompt_driver, MockPromptDriver)

    def test_missing_prompt_driver(self):
        task = PromptTask("test")

        with pytest.raises(ValueError):
            task.prompt_driver
