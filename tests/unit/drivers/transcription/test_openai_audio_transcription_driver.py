from unittest.mock import Mock

import pytest

from griptape.artifacts import AudioArtifact
from griptape.drivers.audio_transcription.openai import OpenAiAudioTranscriptionDriver


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

    def test_try_run_extra_params(self, audio_artifact):
        driver = OpenAiAudioTranscriptionDriver(
            model="model", client=Mock(), api_key="key", extra_params={"language": "en", "temperature": 0.2}
        )
        driver.client.audio.transcriptions.create.return_value = Mock(text="text data")

        driver.try_run(audio_artifact, prompts=["foo", "bar"])

        kwargs = driver.client.audio.transcriptions.create.call_args.kwargs
        assert kwargs["model"] == "model"
        assert kwargs["file"][0] == "a.mp3"
        assert kwargs["response_format"] == "json"
        assert kwargs["prompt"] == "foo, bar"
        assert kwargs["language"] == "en"
        assert kwargs["temperature"] == 0.2
