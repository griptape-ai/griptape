from unittest.mock import Mock

import pytest

from griptape.drivers import ElevenLabsTextToSpeechDriver


class TestElevenLabsTextToSpeechDriver:
    @pytest.fixture()
    def driver(self):
        return ElevenLabsTextToSpeechDriver(model="model", client=Mock(), voice="voice", api_key="key")

    def test_init(self, driver):
        assert driver

    def test_try_text_to_audio(self, driver):
        driver.client.generate.return_value = [b"audio data"]

        audio_artifact = driver.try_text_to_audio(prompt="test prompt")

        assert audio_artifact.value == b"audio data"
        assert audio_artifact.format == "mp3"
