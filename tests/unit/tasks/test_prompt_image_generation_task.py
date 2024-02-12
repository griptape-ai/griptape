from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from unittest.mock import Mock

import pytest

from griptape.artifacts import TextArtifact
from griptape.engines import PromptImageGenerationEngine
from griptape.structures import Agent
from griptape.tasks import BaseTask, PromptImageGenerationTask
from tests.mocks.mock_structure_config import MockStructureConfig


class TestPromptImageGenerationTask:
    def test_string_input(self):
        task = PromptImageGenerationTask("string input", image_generation_engine=Mock())

        assert task.input.value == "string input"

    def test_callable_input(self):
        input_artifact = TextArtifact("some text input")

        def callable(task: BaseTask) -> TextArtifact:
            return input_artifact

        task = PromptImageGenerationTask(callable, image_generation_engine=Mock())

        assert task.input == input_artifact

    def test_config_image_generation_engine_engine(self):
        task = PromptImageGenerationTask("foo bar")
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.image_generation_engine, PromptImageGenerationEngine)
        assert isinstance(task.image_generation_engine.image_generation_driver, MockImageGenerationDriver)

    def test_missing_summary_engine(self):
        task = PromptImageGenerationTask("foo bar")

        with pytest.raises(ValueError):
            task.image_generation_engine
