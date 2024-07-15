import pytest

from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import ActionResultMessageContent, ToolAction


class TestActionResultMessageContent:
    def test_init(self):
        assert (
            ActionResultMessageContent(
                TextArtifact("foo"),
                action=ToolAction(tag="TestTag", name="TestName", path="TestPath", input={"foo": "bar"}),
            ).artifact.value
            == "foo"
        )

    def test_from_deltas(self):
        with pytest.raises(NotImplementedError):
            ActionResultMessageContent.from_deltas([])
