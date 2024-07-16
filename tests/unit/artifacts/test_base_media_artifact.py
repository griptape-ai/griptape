import pytest
from attrs import define

from griptape.artifacts import MediaArtifact


class TestMediaArtifact:
    @define
    class ImaginaryMediaArtifact(MediaArtifact):
        media_type: str = "imagination"

    @pytest.fixture()
    def media_artifact(self):
        return self.ImaginaryMediaArtifact(value=b"some binary dream data", format="dream")

    def test_to_dict(self, media_artifact):
        image_dict = media_artifact.to_dict()

        assert image_dict["format"] == "dream"
        assert image_dict["value"] == "c29tZSBiaW5hcnkgZHJlYW0gZGF0YQ=="

    def test_name(self, media_artifact):
        assert media_artifact.name.startswith("imagination_artifact")
        assert media_artifact.name.endswith(".dream")

    def test_mime_type(self, media_artifact):
        assert media_artifact.mime_type == "imagination/dream"

    def test_to_text(self, media_artifact):
        assert media_artifact.to_text() == "Media, type: imagination/dream, size: 22 bytes"
