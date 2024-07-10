from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import TextMessageContent


class TestBaseMessageContent:
    def test__str__(self):
        assert str(TextMessageContent(TextArtifact("foo"))) == "foo"

    def test__bool__(self):
        assert bool(TextMessageContent(TextArtifact("foo")))
        assert not bool(TextMessageContent(TextArtifact("")))

    def test__len__(self):
        assert len(TextMessageContent(TextArtifact("foo"))) == 3

    def test_to_text(self):
        assert TextMessageContent(TextArtifact("foo")).to_text() == "foo"
