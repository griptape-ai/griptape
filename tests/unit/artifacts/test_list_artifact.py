import pytest

from griptape.artifacts import BlobArtifact, ListArtifact, TextArtifact
from griptape.artifacts.image_artifact import ImageArtifact


class TestListArtifact:
    def test_to_text(self):
        assert ListArtifact([TextArtifact("foo"), TextArtifact("bar")]).to_text() == "foo\n\nbar"
        assert ListArtifact([TextArtifact("foo"), TextArtifact("bar")], item_separator="test").to_text() == "footestbar"

    def test_to_dict(self):
        assert ListArtifact([TextArtifact("foobar")]).to_dict()["value"][0]["value"] == "foobar"

    def test__getitem__(self):
        assert ListArtifact([TextArtifact("foo"), TextArtifact("bar")])[0].value == "foo"
        assert ListArtifact([TextArtifact("foo"), TextArtifact("bar")])[1].value == "bar"

    def test___add__(self):
        artifact = ListArtifact([TextArtifact("foo")]) + ListArtifact([TextArtifact("bar")])

        assert isinstance(artifact, ListArtifact)
        assert len(artifact) == 2
        assert artifact.value[0].value == "foo"
        assert artifact.value[1].value == "bar"

    def test___iter__(self):
        assert [a.value for a in ListArtifact([TextArtifact("foo"), TextArtifact("bar")])] == ["foo", "bar"]

    def test_type_var(self):
        assert ListArtifact[TextArtifact]([TextArtifact("foo")]).value[0].value == "foo"

    def test_validate_value(self):
        with pytest.raises(ValueError):
            ListArtifact([TextArtifact("foo"), BlobArtifact(b"bar")], validate_uniform_types=True)

    def test_child_type(self):
        assert ListArtifact([TextArtifact("foo")]).child_type == TextArtifact

    def test_is_type(self):
        assert ListArtifact([TextArtifact("foo")]).is_type(TextArtifact)
        assert ListArtifact([ImageArtifact(b"", width=1234, height=1234, format="png")]).is_type(ImageArtifact)

    def test_has_items(self):
        assert not ListArtifact().has_items()
        assert ListArtifact([TextArtifact("foo")]).has_items()
