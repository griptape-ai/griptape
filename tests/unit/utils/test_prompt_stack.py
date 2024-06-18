import pytest

from griptape.common import PromptStack


class TestPromptStack:
    @pytest.fixture
    def prompt_stack(self):
        return PromptStack()

    def test_init(self):
        assert PromptStack()

    def test_add_message(self, prompt_stack):
        prompt_stack.add_message("foo", "role")

        assert prompt_stack.messages[0].role == "role"
        assert prompt_stack.messages[0].content[0].artifact.value == "foo"

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
