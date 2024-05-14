from unittest.mock import Mock

from griptape.artifacts import TextArtifact
from griptape.engines import TextToSpeechEngine
from griptape.structures import Agent
from griptape.tasks import BaseTask, TextToSpeechTask
from tests.mocks.mock_structure_config import MockStructureConfig


class TestTextToSpeechTask:
    def test_string_input(self):
        task = TextToSpeechTask("string input", text_to_speech_engine=Mock())

        assert task.input.value == "string input"

    def test_callable_input(self):
        input_artifact = TextArtifact("some text input")

        def callable(task: BaseTask) -> TextArtifact:
            return input_artifact

        task = TextToSpeechTask(callable, text_to_speech_engine=Mock())

        assert task.input == input_artifact

    def test_config_text_to_speech_engine(self):
        task = TextToSpeechTask("foo bar")
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.text_to_speech_engine, TextToSpeechEngine)
