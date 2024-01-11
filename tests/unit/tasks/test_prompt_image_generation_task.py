from unittest.mock import Mock

from griptape.tasks import PromptImageGenerationTask, BaseTask
from griptape.artifacts import TextArtifact


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
