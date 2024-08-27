import pytest

from griptape.artifacts import AudioArtifact, BaseArtifact


class TestAudioArtifact:
    @pytest.fixture()
    def audio_artifact(self):
        return AudioArtifact(
            value=b"some binary audio data", format="pcm", meta={"model": "provider/model", "prompt": "two words"}
        )

    def test_mime_type(self, audio_artifact: AudioArtifact):
        assert audio_artifact.mime_type == "audio/pcm"

    def test_to_text(self, audio_artifact: AudioArtifact):
        assert audio_artifact.to_text() == "Audio, format: pcm, size: 22 bytes"

    def test_to_dict(self, audio_artifact: AudioArtifact):
        audio_dict = audio_artifact.to_dict()

        assert audio_dict["format"] == "pcm"
        assert audio_dict["meta"]["model"] == "provider/model"
        assert audio_dict["meta"]["prompt"] == "two words"
        assert audio_dict["value"] == "c29tZSBiaW5hcnkgYXVkaW8gZGF0YQ=="

    def test_deserialization(self, audio_artifact):
        artifact_dict = audio_artifact.to_dict()
        deserialized_artifact = BaseArtifact.from_dict(artifact_dict)

        assert isinstance(deserialized_artifact, AudioArtifact)

        assert deserialized_artifact.value == b"some binary audio data"
        assert deserialized_artifact.mime_type == "audio/pcm"
        assert deserialized_artifact.format == "pcm"
        assert deserialized_artifact.meta["model"] == "provider/model"
        assert deserialized_artifact.meta["prompt"] == "two words"
