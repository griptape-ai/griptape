import pytest

from griptape.artifacts.action_artifact import ActionArtifact
from griptape.common import ActionCallDeltaMessageContent, ActionCallMessageContent, ToolAction


class TestActionCallMessageContent:
    def test_init(self):
        assert ActionCallMessageContent(
            ActionArtifact(ToolAction(tag="TestTag", name="TestName", path="TestPath", input={"foo": "bar"}))
        ).artifact.value.to_dict() == {
            "type": "ToolAction",
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
        }

    def test_from_deltas(self):
        deltas = [
            ActionCallDeltaMessageContent(tag="testtag"),
            ActionCallDeltaMessageContent(name="TestName"),
            ActionCallDeltaMessageContent(path="test_tag"),
            ActionCallDeltaMessageContent(partial_input='{"foo":'),
            ActionCallDeltaMessageContent(partial_input='"bar"}'),
        ]

        assert ActionCallMessageContent.from_deltas(deltas).artifact.value.to_dict() == {
            "type": "ToolAction",
            "tag": "testtag",
            "name": "TestName",
            "path": "test_tag",
            "input": {"foo": "bar"},
        }

    def test_from_missing_header(self):
        deltas = [
            ActionCallDeltaMessageContent(tag="testtag"),
            ActionCallDeltaMessageContent(name="TestName"),
            ActionCallDeltaMessageContent(partial_input='{"foo":'),
            ActionCallDeltaMessageContent(partial_input='"bar"}'),
        ]

        with pytest.raises(ValueError, match="Missing required fields"):
            ActionCallMessageContent.from_deltas(deltas)

    def test_from_bad_json(self):
        deltas = [
            ActionCallDeltaMessageContent(tag="testtag"),
            ActionCallDeltaMessageContent(name="TestName"),
            ActionCallDeltaMessageContent(path="test_tag"),
            ActionCallDeltaMessageContent(partial_input='{"foo":'),
        ]

        with pytest.raises(ValueError, match="Invalid JSON"):
            ActionCallMessageContent.from_deltas(deltas)
