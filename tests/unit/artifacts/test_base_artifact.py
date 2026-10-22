import pytest

from griptape.artifacts import (
    BaseArtifact,
    BlobArtifact,
    ErrorArtifact,
    ImageArtifact,
    InfoArtifact,
    ListArtifact,
    TextArtifact,
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
        dict_value = {"type": "BlobArtifact", "value": b"Zm9vYmFy", "name": "bar"}
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, BlobArtifact)
        assert artifact.to_text() == "foobar"

    def test_image_artifact_from_dict(self):
        dict_value = {
            "type": "ImageArtifact",
            "value": b"aW1hZ2UgZGF0YQ==",
            "format": "png",
            "width": 256,
            "height": 256,
            "meta": {"model": "test-model", "prompt": "some prompt"},
        }
        artifact = BaseArtifact.from_dict(dict_value)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.to_text() == "Image, format: png, size: 10 bytes"
        assert artifact.value == b"image data"

    def test_unsupported_from_dict(self):
        dict_value = {"type": "foo", "value": "foobar"}
        with pytest.raises(ValueError):
            BaseArtifact.from_dict(dict_value)

    def test_equality_ignores_generated_id_and_name(self):
        assert TextArtifact("foo") == TextArtifact("foo")
        assert TextArtifact("foo", id="a", name="a") == TextArtifact("foo", id="b", name="b")
        assert ImageArtifact(b"data", format="png", width=1, height=1) == ImageArtifact(
            b"data", format="png", width=1, height=1
        )

    def test_equality_compares_content(self):
        assert TextArtifact("foo") != TextArtifact("bar")
        assert TextArtifact("foo", meta={"a": 1}) != TextArtifact("foo", meta={"a": 2})
        assert TextArtifact("foo") != InfoArtifact("foo")
