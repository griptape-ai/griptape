from unittest.mock import Mock

import pytest

from griptape.artifacts import AudioArtifact
from griptape.engines import AudioTranscriptionEngine
from griptape.structures import Agent
from griptape.tasks import BaseTask, AudioTranscriptionTask
from tests.mocks.mock_structure_config import MockStructureConfig


class TestAudioTranscriptionTask:
    @pytest.fixture
    def audio_artifact(self):
        return AudioArtifact(value=b"audio data", format="mp3")

    @pytest.fixture
    def audio_transcription_engine(self):
        return Mock()

    def test_audio_input(self, audio_artifact, audio_transcription_engine):
        task = AudioTranscriptionTask(audio_artifact, audio_transcription_engine=audio_transcription_engine)

        assert task.input.value == audio_artifact.value

    def test_callable_input(self, audio_artifact, audio_transcription_engine):
        def callable(task: BaseTask) -> AudioArtifact:
            return audio_artifact

        task = AudioTranscriptionTask(callable, audio_transcription_engine=audio_transcription_engine)

        assert task.input == audio_artifact

    def test_config_audio_transcription_engine(self, audio_artifact):
        task = AudioTranscriptionTask(audio_artifact)
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.audio_transcription_engine, AudioTranscriptionEngine)
