import pytest
from griptape.utils import PromptStack


class TestPromptStack:
    @pytest.fixture
    def prompt_stack(self):
        return PromptStack()

    def test_init(self):
        assert PromptStack()

    def test_add_input(self, prompt_stack):
        prompt_stack.add_input("foo", "role")

        assert prompt_stack.inputs[0].role == "role"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_generic_input(self, prompt_stack):
        prompt_stack.add_generic_input("foo")

        assert prompt_stack.inputs[0].role == "generic"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_system_input(self, prompt_stack):
        prompt_stack.add_system_input("foo")

        assert prompt_stack.inputs[0].role == "system"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_user_input(self, prompt_stack):
        prompt_stack.add_user_input("foo")

        assert prompt_stack.inputs[0].role == "user"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_assistant_input(self, prompt_stack):
        prompt_stack.add_assistant_input("foo")

        assert prompt_stack.inputs[0].role == "assistant"
        assert prompt_stack.inputs[0].content == "foo"
