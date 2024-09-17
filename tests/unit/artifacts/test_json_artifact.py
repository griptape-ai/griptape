import json

from griptape.artifacts import JsonArtifact


class TestJsonArtifact:
    def test_value_type_conversion(self):
        assert JsonArtifact({"foo": "bar"}).value == json.loads(json.dumps({"foo": "bar"}))
        assert JsonArtifact({"foo": 1}).value == json.loads(json.dumps({"foo": 1}))
        assert JsonArtifact({"foo": 1.0}).value == json.loads(json.dumps({"foo": 1.0}))
        assert JsonArtifact({"foo": True}).value == json.loads(json.dumps({"foo": True}))
        assert JsonArtifact({"foo": None}).value == json.loads(json.dumps({"foo": None}))
        assert JsonArtifact([{"foo": {"bar": "baz"}}]).value == json.loads(json.dumps([{"foo": {"bar": "baz"}}]))
        assert JsonArtifact(None).value == json.loads(json.dumps(None))
        assert JsonArtifact('"foo"').value == "foo"
        assert JsonArtifact("true").value is True
        assert JsonArtifact("false").value is False
        assert JsonArtifact("123").value == 123
        assert JsonArtifact("123.4").value == 123.4

    def test_to_text(self):
        assert JsonArtifact({"foo": "bar"}).to_text() == json.dumps({"foo": "bar"})
        assert JsonArtifact({"foo": 1}).to_text() == json.dumps({"foo": 1})
        assert JsonArtifact({"foo": 1.0}).to_text() == json.dumps({"foo": 1.0})
        assert JsonArtifact({"foo": True}).to_text() == json.dumps({"foo": True})
        assert JsonArtifact({"foo": None}).to_text() == json.dumps({"foo": None})
        assert JsonArtifact([{"foo": {"bar": "baz"}}]).to_text() == json.dumps([{"foo": {"bar": "baz"}}])
