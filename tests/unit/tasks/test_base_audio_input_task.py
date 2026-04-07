import pytest

from griptape.artifacts import AudioArtifact, TextArtifact
from tests.mocks.mock_audio_input_task import MockAudioInputTask
from tests.mocks.mock_text_input_task import MockTextInputTask


class TestBaseAudioInputTask:
    @pytest.fixture()
    def audio_artifact(self):
        return AudioArtifact(b"audio content", format="mp3")

    def test_audio_artifact_input(self, audio_artifact):
        task = MockAudioInputTask(audio_artifact)
        assert task.input.value == audio_artifact.value

        audio_artifact.value = b"new audio content"
        task.input = audio_artifact
        assert task.input.value == audio_artifact.value

    def test_callable_input(self, audio_artifact):
        assert MockTextInputTask(lambda _: audio_artifact).input.value == audio_artifact.value

    def test_bad_input(self):
        with pytest.raises(ValueError):
            assert MockAudioInputTask(TextArtifact("foobar")).input.value == "foobar"
