import pytest

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.common import ImageMessageContent, PromptStack, TextMessageContent


class TestPromptStack:
    @pytest.fixture()
    def prompt_stack(self):
        return PromptStack()

    def test_init(self):
        assert PromptStack()

    def test_add_message(self, prompt_stack):
        prompt_stack.add_message("foo", "role")
        prompt_stack.add_message(TextArtifact("foo"), "role")
        prompt_stack.add_message(ImageArtifact(b"foo", format="png", width=100, height=100), "role")
        prompt_stack.add_message(ListArtifact([TextArtifact("foo"), TextArtifact("bar")]), "role")

        assert prompt_stack.messages[0].role == "role"
        assert isinstance(prompt_stack.messages[0].content[0], TextMessageContent)
        assert prompt_stack.messages[0].content[0].artifact.value == "foo"

        assert prompt_stack.messages[1].role == "role"
        assert isinstance(prompt_stack.messages[1].content[0], TextMessageContent)
        assert prompt_stack.messages[1].content[0].artifact.value == "foo"

        assert prompt_stack.messages[2].role == "role"
        assert isinstance(prompt_stack.messages[2].content[0], ImageMessageContent)
        assert prompt_stack.messages[2].content[0].artifact.value == b"foo"

        assert prompt_stack.messages[3].role == "role"
        assert isinstance(prompt_stack.messages[3].content[0], TextMessageContent)
        assert prompt_stack.messages[3].content[0].artifact.value == "foo"
        assert isinstance(prompt_stack.messages[3].content[1], TextMessageContent)
        assert prompt_stack.messages[3].content[1].artifact.value == "bar"

    def test_add_system_message(self, prompt_stack):
        prompt_stack.add_system_message("foo")

        assert prompt_stack.messages[0].role == "system"
        assert prompt_stack.messages[0].content[0].artifact.value == "foo"

    def test_add_user_message(self, prompt_stack):
        prompt_stack.add_user_message("foo")

        assert prompt_stack.messages[0].role == "user"
        assert prompt_stack.messages[0].content[0].artifact.value == "foo"

    def test_add_assistant_message(self, prompt_stack):
        prompt_stack.add_assistant_message("foo")

        assert prompt_stack.messages[0].role == "assistant"
        assert prompt_stack.messages[0].content[0].artifact.value == "foo"
