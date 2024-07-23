import json

from griptape.artifacts import BaseArtifact, TextArtifact


class TestTextArtifact:
    def test_value_type_conversion(self):
        assert TextArtifact("1").value == "1"
        assert TextArtifact(1).value == "1"

    def test___add__(self):
        assert (TextArtifact("foo") + TextArtifact("bar")).value == "foobar"

    def test_to_dict(self):
        assert TextArtifact("foobar").to_dict()["value"] == "foobar"

    def test_from_dict(self):
        assert BaseArtifact.from_dict(TextArtifact("foobar").to_dict()).value == "foobar"

    def test_to_json(self):
        assert json.loads(TextArtifact("foobar").to_json())["value"] == "foobar"

    def test_from_json(self):
        assert BaseArtifact.from_json(TextArtifact("foobar").to_json()).value == "foobar"

    def test_name(self):
        artifact = TextArtifact("foo")

        assert artifact.name == artifact.id
        assert TextArtifact("foo", name="bar").name == "bar"

    def test_meta(self):
        artifact = TextArtifact("foo")

        assert artifact.meta == {}

        meta = {"foo": "bar"}
        assert TextArtifact("foo", meta=meta).meta == meta
