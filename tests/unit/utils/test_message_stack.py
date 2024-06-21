import pytest

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.common import ImageMessageContent, MessageStack, TextMessageContent


class TestPromptStack:
    @pytest.fixture
    def message_stack(self):
        return MessageStack()

    def test_init(self):
        assert MessageStack()

    def test_add_message(self, message_stack):
        message_stack.add_message("foo", "role")
        message_stack.add_message(TextArtifact("foo"), "role")
        message_stack.add_message(ImageArtifact(b"foo", format="png", width=100, height=100), "role")
        message_stack.add_message(ListArtifact([TextArtifact("foo"), TextArtifact("bar")]), "role")

        assert message_stack.messages[0].role == "role"
        assert isinstance(message_stack.messages[0].content[0], TextMessageContent)
        assert message_stack.messages[0].content[0].artifact.value == "foo"

        assert message_stack.messages[1].role == "role"
        assert isinstance(message_stack.messages[1].content[0], TextMessageContent)
        assert message_stack.messages[1].content[0].artifact.value == "foo"

        assert message_stack.messages[2].role == "role"
        assert isinstance(message_stack.messages[2].content[0], ImageMessageContent)
        assert message_stack.messages[2].content[0].artifact.value == b"foo"

        assert message_stack.messages[3].role == "role"
        assert isinstance(message_stack.messages[3].content[0], TextMessageContent)
        assert message_stack.messages[3].content[0].artifact.value == "foo"
        assert isinstance(message_stack.messages[3].content[1], TextMessageContent)
        assert message_stack.messages[3].content[1].artifact.value == "bar"

    def test_add_system_message(self, message_stack):
        message_stack.add_system_message("foo")

        assert message_stack.messages[0].role == "system"
        assert message_stack.messages[0].content[0].artifact.value == "foo"

    def test_add_user_message(self, message_stack):
        message_stack.add_user_message("foo")

        assert message_stack.messages[0].role == "user"
        assert message_stack.messages[0].content[0].artifact.value == "foo"

    def test_add_assistant_message(self, message_stack):
        message_stack.add_assistant_message("foo")

        assert message_stack.messages[0].role == "assistant"
        assert message_stack.messages[0].content[0].artifact.value == "foo"
