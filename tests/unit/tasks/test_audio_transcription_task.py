from unittest.mock import Mock

import pytest

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.drivers.audio_transcription import BaseAudioTranscriptionDriver
from griptape.structures import Agent, Pipeline
from griptape.tasks import AudioTranscriptionTask, BaseTask


class TestAudioTranscriptionTask:
    @pytest.fixture()
    def audio_artifact(self):
        return AudioArtifact(value=b"audio data", format="mp3")

    @pytest.fixture()
    def audio_transcription_driver(self):
        return Mock()

    def test_audio_input(self, audio_artifact, audio_transcription_driver):
        task = AudioTranscriptionTask(audio_artifact, audio_transcription_driver=audio_transcription_driver)

        assert task.input.value == audio_artifact.value

    def test_callable_input(self, audio_artifact, audio_transcription_driver):
        def callable_input(task: BaseTask) -> AudioArtifact:
            return audio_artifact

        task = AudioTranscriptionTask(callable_input, audio_transcription_driver=audio_transcription_driver)

        assert task.input == audio_artifact

    def test_config_audio_transcription_driver(self, audio_artifact):
        task = AudioTranscriptionTask(audio_artifact)
        Agent().add_task(task)

        assert isinstance(task.audio_transcription_driver, BaseAudioTranscriptionDriver)

    def test_run(self, audio_artifact, audio_transcription_driver):
        audio_transcription_driver.run.return_value = TextArtifact("mock transcription")

        task = AudioTranscriptionTask(audio_artifact, audio_transcription_driver=audio_transcription_driver)
        pipeline = Pipeline()
        pipeline.add_task(task)

        assert pipeline.run().output.to_text() == "mock transcription"
