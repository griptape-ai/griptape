from unittest.mock import Mock

import pytest

from griptape.artifacts import AudioArtifact
from griptape.events import EventBus, EventListener
from tests.mocks.mock_audio_transcription_driver import MockAudioTranscriptionDriver


class TestBaseAudioTranscriptionDriver:
    @pytest.fixture()
    def driver(self):
        return MockAudioTranscriptionDriver()

    def test_run_publish_events(self, driver, mock_config):
        mock_handler = Mock()
        EventBus.add_event_listener(EventListener(handler=mock_handler))

        driver.run(
            AudioArtifact(
                value="audio",
                format="audio/wav",
            ),
            ["foo", "bar"],
        )

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartAudioTranscriptionEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishAudioTranscriptionEvent"
