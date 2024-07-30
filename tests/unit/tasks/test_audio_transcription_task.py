from unittest.mock import Mock

import pytest

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.engines import AudioTranscriptionEngine
from griptape.structures import Agent, Pipeline
from griptape.tasks import AudioTranscriptionTask, BaseTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_structure_config import MockStructureConfig


class TestAudioTranscriptionTask:
    @pytest.fixture()
    def audio_artifact(self):
        return AudioArtifact(value=b"audio data", format="mp3")

    @pytest.fixture()
    def audio_transcription_engine(self):
        return Mock()

    def test_audio_input(self, audio_artifact, audio_transcription_engine):
        task = AudioTranscriptionTask(audio_artifact, audio_transcription_engine=audio_transcription_engine)

        assert task.input.value == audio_artifact.value

    def test_callable_input(self, audio_artifact, audio_transcription_engine):
        def callable_input(task: BaseTask) -> AudioArtifact:
            return audio_artifact

        task = AudioTranscriptionTask(callable_input, audio_transcription_engine=audio_transcription_engine)

        assert task.input == audio_artifact

    def test_config_audio_transcription_engine(self, audio_artifact):
        task = AudioTranscriptionTask(audio_artifact)
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.audio_transcription_engine, AudioTranscriptionEngine)

    def test_run(self, audio_artifact, audio_transcription_engine):
        audio_transcription_engine.run.return_value = TextArtifact("mock transcription")

        task = AudioTranscriptionTask(audio_artifact, audio_transcription_engine=audio_transcription_engine)
        pipeline = Pipeline(prompt_driver=MockPromptDriver())
        pipeline.add_task(task)

        assert pipeline.run().output.to_text() == "mock transcription"
