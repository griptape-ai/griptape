from unittest.mock import Mock

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.drivers.text_to_speech.base_text_to_speech_driver import BaseTextToSpeechDriver
from griptape.structures import Agent, Pipeline
from griptape.tasks import BaseTask, TextToSpeechTask


class TestTextToSpeechTask:
    def test_string_input(self):
        task = TextToSpeechTask("string input", text_to_speech_driver=Mock())

        assert task.input.value == "string input"

    def test_callable_input(self):
        input_artifact = TextArtifact("some text input")

        def callable_input(task: BaseTask) -> TextArtifact:
            return input_artifact

        task = TextToSpeechTask(callable_input, text_to_speech_driver=Mock())

        assert task.input == input_artifact

    def test_config_text_to_speech_driver(self):
        task = TextToSpeechTask("foo bar")
        Agent().add_task(task)

        assert isinstance(task.text_to_speech_driver, BaseTextToSpeechDriver)

    def test_calls(self):
        text_to_speech_driver = Mock()
        text_to_speech_driver.run_text_to_audio.return_value = AudioArtifact(b"audio content", format="mp3")

        assert TextToSpeechTask("test", text_to_speech_driver=text_to_speech_driver).run().value == b"audio content"

    def test_run(self):
        text_to_speech_driver = Mock()
        text_to_speech_driver.run_text_to_audio.return_value = AudioArtifact(b"audio content", format="mp3")

        task = TextToSpeechTask("some text", text_to_speech_driver=text_to_speech_driver)
        pipeline = Pipeline()
        pipeline.add_task(task)

        assert isinstance(pipeline.run().output, AudioArtifact)
