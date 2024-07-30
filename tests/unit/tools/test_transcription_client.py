from unittest.mock import Mock, mock_open, patch

import pytest

from griptape.artifacts import AudioArtifact
from griptape.tools.audio_transcription_client.tool import AudioTranscriptionClient


class TestTranscriptionClient:
    @pytest.fixture()
    def transcription_engine(self) -> Mock:
        return Mock()

    @pytest.fixture()
    def audio_loader(self) -> Mock:
        loader = Mock()
        loader.load.return_value = AudioArtifact(value=b"audio data", format="wav")

        return loader

    @pytest.fixture(
        autouse=True,
    )
    def mock_path(self, mocker) -> Mock:
        mocker.patch("pathlib.Path.read_bytes", return_value=b"transcription")

        return mocker

    def test_init_transcription_client(self, transcription_engine, audio_loader) -> None:
        assert AudioTranscriptionClient(engine=transcription_engine, audio_loader=audio_loader)

    @patch("builtins.open", mock_open(read_data=b"audio data"))
    def test_transcribe_audio_from_disk(self, transcription_engine, audio_loader) -> None:
        client = AudioTranscriptionClient(engine=transcription_engine, audio_loader=audio_loader)
        client.engine.run.return_value = Mock(value="transcription")  # pyright: ignore[reportFunctionMemberAccess]

        text_artifact = client.transcribe_audio_from_disk(params={"values": {"path": "audio.wav"}})

        assert text_artifact
        assert text_artifact.value == "transcription"

    def test_transcribe_audio_from_memory(self, transcription_engine, audio_loader) -> None:
        client = AudioTranscriptionClient(engine=transcription_engine, audio_loader=audio_loader)
        memory = Mock()
        memory.load_artifacts = Mock(return_value=[AudioArtifact(value=b"audio data", format="wav", name="name")])
        client.find_input_memory = Mock(return_value=memory)

        client.engine.run.return_value = Mock(value="transcription")  # pyright: ignore[reportFunctionMemberAccess]

        text_artifact = client.transcribe_audio_from_memory(
            params={"values": {"memory_name": "memory", "artifact_namespace": "namespace", "artifact_name": "name"}}
        )

        assert text_artifact
        assert text_artifact.value == "transcription"
