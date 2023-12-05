import pytest
from griptape.events import FinishPromptEvent
from griptape.utils import PromptStack


class TestFinishPromptEvent:
    @pytest.fixture
    def finish_prompt_event(self):
        prompt_stack = PromptStack()
        prompt_stack.add_user_input("foo")
        prompt_stack.add_system_input("bar")
        return FinishPromptEvent(token_count=123, prompt_stack=prompt_stack, prompt="foo bar")

    def test_to_dict(self, finish_prompt_event):
        assert "timestamp" in finish_prompt_event.to_dict()

        assert finish_prompt_event.to_dict()["token_count"] == 123
        assert finish_prompt_event.to_dict()["prompt_stack"]["inputs"][0]["content"] == "foo"
        assert finish_prompt_event.to_dict()["prompt_stack"]["inputs"][0]["role"] == "user"
        assert finish_prompt_event.to_dict()["prompt_stack"]["inputs"][1]["content"] == "bar"
        assert finish_prompt_event.to_dict()["prompt_stack"]["inputs"][1]["role"] == "system"

        assert finish_prompt_event.to_dict()["prompt"] == "foo bar"
