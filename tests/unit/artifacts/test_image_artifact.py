import pytest
from griptape.artifacts import ImageArtifact, BaseArtifact


class TestImageArtifact:
    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(
            value=b"some binary png image data",
            mime_type="image/png",
            width=512,
            height=512,
            model="openai/dalle2",
            prompt="a cute cat",
        )

    def test_to_text(self, image_artifact):
        assert image_artifact.to_text() == "Image, dimensions: 512x512, type: image/png, size: 26 bytes"

    def test_to_dict(self, image_artifact):
        image_dict = image_artifact.to_dict()

        assert image_dict["mime_type"] == "image/png"
        assert image_dict["width"] == 512
        assert image_dict["height"] == 512
        assert image_dict["model"] == "openai/dalle2"
        assert image_dict["prompt"] == "a cute cat"
        assert image_dict["value"] == "c29tZSBiaW5hcnkgcG5nIGltYWdlIGRhdGE="

    def test_deserialization(self, image_artifact):
        artifact_dict = image_artifact.to_dict()
        deserialized_artifact = BaseArtifact.from_dict(artifact_dict)

        assert isinstance(deserialized_artifact, ImageArtifact)

        assert deserialized_artifact.value == b"some binary png image data"
        assert deserialized_artifact.mime_type == "image/png"
        assert deserialized_artifact.width == 512
        assert deserialized_artifact.height == 512
        assert deserialized_artifact.model == "openai/dalle2"
        assert deserialized_artifact.prompt == "a cute cat"
