import pytest
from griptape.artifacts import (
    BaseArtifact,
    TextArtifact,
    ErrorArtifact,
    InfoArtifact,
    ListArtifact,
    BlobArtifact,
    ImageArtifact,
)


class TestBaseArtifact:
    def test_text_artifact_from_dict(self):
        dict_value = {"type": "TextArtifact", "value": "foobar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, TextArtifact)
        assert artifact.to_text() == "foobar"

    def test_error_artifact_from_dict(self):
        dict_value = {"type": "ErrorArtifact", "value": "foobar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, ErrorArtifact)
        assert artifact.to_text() == "foobar"

    def test_info_artifact_from_dict(self):
        dict_value = {"type": "InfoArtifact", "value": "foobar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, InfoArtifact)
        assert artifact.to_text() == "foobar"

    def test_list_artifact_from_dict(self):
        dict_value = {"type": "ListArtifact", "value": [{"type": "TextArtifact", "value": "foobar"}]}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, ListArtifact)
        assert artifact.to_text() == "foobar"

    def test_blob_artifact_from_dict(self):
        dict_value = {"type": "BlobArtifact", "value": b"Zm9vYmFy", "dir_name": "foo", "name": "bar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, BlobArtifact)
        assert artifact.to_text() == "foobar"

    def test_image_artifact_from_dict(self):
        dict_value = {
            "type": "ImageArtifact",
            "value": b"aW1hZ2UgZGF0YQ==",
            "mime_type": "image/png",
            "dir_name": "foo",
            "width": 256,
            "height": 256,
            "model": "test-model",
            "prompt": "some prompt",
        }
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.to_text() == "Image, dimensions: 256x256, type: image/png, size: 10 bytes"
        assert artifact.value == b"image data"

    def test_unsupported_from_dict(self):
        dict_value = {"type": "foo", "value": "foobar"}
        with pytest.raises(ValueError):
            BaseArtifact.from_dict(dict_value)
