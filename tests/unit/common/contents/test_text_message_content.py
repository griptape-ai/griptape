from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import TextMessageContent, TextDeltaMessageContent


class TestTextMessageContent:
    def test_init(self):
        assert TextMessageContent(TextArtifact("foo")).artifact.value == "foo"

    def test_from_deltas(self):
        assert (
            TextMessageContent.from_deltas(
                [TextDeltaMessageContent("foo"), TextDeltaMessageContent("bar")]
            ).artifact.value
            == "foobar"
        )
