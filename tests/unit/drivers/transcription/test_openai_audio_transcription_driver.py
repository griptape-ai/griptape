from unittest.mock import Mock

import pytest

from griptape.artifacts import AudioArtifact
from griptape.drivers import OpenAiAudioTranscriptionDriver


class TestOpenAiAudioTranscriptionDriver:
    @pytest.fixture()
    def audio_artifact(self):
        return AudioArtifact(value=b"audio data", format="mp3")

    @pytest.fixture()
    def driver(self):
        return OpenAiAudioTranscriptionDriver(model="model", client=Mock(), api_key="key")

    def test_init(self, driver):
        assert driver

    def test_try_text_to_audio(self, driver, audio_artifact):
        driver.client.audio.transcriptions.create.return_value = Mock(text="text data")

        text_artifact = driver.try_run(audio_artifact)

        assert text_artifact.value == "text data"
