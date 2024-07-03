import json
import pytest
from griptape.artifacts import JsonArtifact, TextArtifact


class TestJsonArtifact:
    def test_value_type_conversion(self):
        assert JsonArtifact({"foo": "bar"}).value == json.loads(json.dumps({"foo": "bar"}))
        string = json.dumps({"foo": {}})
        print(string)
        string = json.loads(string)
        print(string)

    def test___add__(self):
        assert JsonArtifact({"foo": "bar"}) + JsonArtifact({"value": "baz"}) == JsonArtifact(
            {"foo": "bar", "value": "baz"}
        )

        new = JsonArtifact({"foo": "bar"}) + JsonArtifact({"value": "baz"})
        assert new == {"foo": "bar", "value": "baz"}

        assert JsonArtifact({"foo": "bar"}) + JsonArtifact({"foo": "baz"}) == JsonArtifact({"foo": "baz"})
        with pytest.raises(ValueError):
            JsonArtifact({"foo": "bar"}) + TextArtifact("invalid json")

    def test___eq__(self):
        assert JsonArtifact({"foo": "bar"}) == json.dumps({"foo": "bar"})
        assert JsonArtifact({"foo": "bar"}) == {"foo": "bar"}

    def test_to_text(self):
        assert JsonArtifact({"foo": "bar"}).to_text() == json.dumps({"foo": "bar"})

    def test_to_bytes_encoding(self):
        assert JsonArtifact({"foo": "bar"}).to_bytes() == json.dumps({"foo": "bar"}).encode()
