import pytest

from griptape.drivers.parser.audio_parser_driver import AudioParserDriver


class TestAudioParserDriver:
    @pytest.fixture()
    def driver(self):
        return AudioParserDriver()

    def test_parse(self, driver):
        data = b"test"
        result = driver.parse(data, {"mime_type": "audio/foo"})
        assert result.value == data
        assert result.format == "foo"
