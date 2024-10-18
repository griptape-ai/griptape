from unittest.mock import Mock

from griptape.artifacts import AudioArtifact, ListArtifact, TextArtifact
from griptape.engines import TextToSpeechEngine
from griptape.structures import Agent, Pipeline
from griptape.tasks import BaseTask, TextToSpeechTask


class TestTextToSpeechTask:
    def test_string_input(self):
        task = TextToSpeechTask("string input", text_to_speech_engine=Mock())

        assert task.input.value == "string input"

    def test_callable_input(self):
        input_artifact = TextArtifact("some text input")

        def callable_input(task: BaseTask) -> TextArtifact:
            return input_artifact

        task = TextToSpeechTask(callable_input, text_to_speech_engine=Mock())

        assert task.input == input_artifact

    def test_config_text_to_speech_engine(self):
        task = TextToSpeechTask("foo bar")
        Agent().add_task(task)

        assert isinstance(task.text_to_speech_engine, TextToSpeechEngine)

    def test_calls(self):
        text_to_speech_engine = Mock()
        text_to_speech_engine.run.return_value = ListArtifact([AudioArtifact(b"audio content", format="mp3")])

        assert TextToSpeechTask("test", text_to_speech_engine=text_to_speech_engine).run()[0].value == b"audio content"

    def test_run(self):
        text_to_speech_engine = Mock()
        text_to_speech_engine.run.return_value = ListArtifact([AudioArtifact(b"audio content", format="mp3")])

        task = TextToSpeechTask("some text", text_to_speech_engine=text_to_speech_engine)
        pipeline = Pipeline()
        pipeline.add_task(task)

        assert isinstance(pipeline.run().output, ListArtifact)
        assert isinstance(pipeline.run().output[0], AudioArtifact)  # pyright: ignore[reportIndexIssue, reportOptionalSubscript]
