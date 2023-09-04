import pytest
from griptape.artifacts import ListArtifact, TextArtifact, BlobArtifact


class TestListArtifact:
    def test_to_text(self):
        assert ListArtifact([TextArtifact("foo"), TextArtifact("bar")]).to_text() == "foo\n\nbar"

    def test_to_dict(self):
        assert ListArtifact([TextArtifact("foobar")]).to_dict()["value"][0]["value"] == "foobar"

    def test___add__(self):
        artifact = ListArtifact([TextArtifact("foo")]) + ListArtifact([TextArtifact("bar")])

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 2
        assert artifact.value[0].value == "foo"
        assert artifact.value[1].value == "bar"

    def test_validate_value(self):
        with pytest.raises(ValueError):
            ListArtifact([TextArtifact("foo"), BlobArtifact(b"bar")])
