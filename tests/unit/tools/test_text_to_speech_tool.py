import os
import tempfile
import uuid
from unittest.mock import Mock

import pytest

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.tools.text_to_speech.tool import TextToSpeechTool


class TestTextToSpeechTool:
    @pytest.fixture()
    def text_to_speech_engine(self) -> Mock:
        return Mock()

    @pytest.fixture()
    def text_to_speech_client(self, text_to_speech_engine) -> TextToSpeechTool:
        return TextToSpeechTool(engine=text_to_speech_engine)

    def test_validate_output_configs(self, text_to_speech_engine) -> None:
        with pytest.raises(ValueError):
            TextToSpeechTool(engine=text_to_speech_engine, output_dir="test", output_file="test")

    def test_text_to_speech(self, text_to_speech_client) -> None:
        text_to_speech_client.engine.run.return_value = Mock(value=b"audio data", format="mp3")

        audio_artifact = text_to_speech_client.text_to_speech(params={"values": {"text": "say this!"}})

        assert audio_artifact

    def test_text_to_speech_with_outfile(self, text_to_speech_engine) -> None:
        outfile = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.mp3"
        text_to_speech_client = TextToSpeechTool(engine=text_to_speech_engine, output_file=outfile)

        text_to_speech_client.engine.run.return_value = AudioArtifact(value=b"audio data", format="mp3")  # pyright: ignore[reportFunctionMemberAccess]

        audio_artifact = text_to_speech_client.text_to_speech(params={"values": {"text": "say this!"}})

        assert audio_artifact
        assert os.path.exists(outfile)
