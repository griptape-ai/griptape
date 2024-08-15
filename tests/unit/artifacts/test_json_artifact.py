import json

import pytest

from griptape.artifacts import JsonArtifact, TextArtifact


class TestJsonArtifact:
    def test_value_type_conversion(self):
        assert JsonArtifact({"foo": "bar"}).value == json.loads(json.dumps({"foo": "bar"}))

    def test___add__(self):
        assert (JsonArtifact({"foo": "bar"}) + JsonArtifact({"value": "baz"})).value == JsonArtifact(
            {"foo": "bar", "value": "baz"}
        ).value

        new = JsonArtifact({"foo": "bar"}) + JsonArtifact({"value": "baz"})
        assert new.value == {"foo": "bar", "value": "baz"}

        assert (JsonArtifact({"foo": "bar"}) + JsonArtifact({"foo": "baz"})).value == JsonArtifact({"foo": "baz"}).value
        with pytest.raises(ValueError):
            JsonArtifact({"foo": "bar"}) + TextArtifact("invalid json")

    def test_to_text(self):
        assert JsonArtifact({"foo": "bar"}).to_text() == json.dumps({"foo": "bar"})
