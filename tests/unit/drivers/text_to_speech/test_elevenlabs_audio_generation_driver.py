from unittest.mock import Mock

import pytest

from griptape.drivers.text_to_speech.elevenlabs import ElevenLabsTextToSpeechDriver


class TestElevenLabsTextToSpeechDriver:
    @pytest.fixture()
    def driver(self):
        return ElevenLabsTextToSpeechDriver(model="model", client=Mock(), voice="voice", api_key="key")

    def test_init(self, driver):
        assert driver

    def test_try_text_to_audio(self, driver):
        driver.client.generate.return_value = [b"audio data"]

        audio_artifact = driver.try_text_to_audio(prompts=["test prompt"])

        assert audio_artifact.value == b"audio data"
        assert audio_artifact.format == "mp3"

    def test_try_text_to_audio_extra_params(self):
        driver = ElevenLabsTextToSpeechDriver(
            model="model",
            client=Mock(),
            voice="voice",
            api_key="key",
            extra_params={"optimize_streaming_latency": 3},
        )
        driver.client.generate.return_value = [b"audio data"]

        driver.try_text_to_audio(prompts=["foo", "bar"])

        driver.client.generate.assert_called_once_with(
            text="foo. bar",
            voice="voice",
            model="model",
            output_format="mp3_44100_128",
            optimize_streaming_latency=3,
        )
