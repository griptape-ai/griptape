from unittest.mock import Mock

import pytest

from griptape.events import EventListener, event_bus
from tests.mocks.mock_text_to_speech_driver import MockTextToSpeechDriver


class TestBaseTextToSpeechDriver:
    @pytest.fixture()
    def driver(self):
        return MockTextToSpeechDriver()

    def test_text_to_audio_publish_events(self, driver):
        mock_handler = Mock()
        event_bus.add_event_listener(EventListener(handler=mock_handler))

        driver.run_text_to_audio(
            ["foo", "bar"],
        )

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartTextToSpeechEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishTextToSpeechEvent"
