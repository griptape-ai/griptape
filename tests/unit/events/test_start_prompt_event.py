import pytest
from griptape.events import StartPromptEvent
from griptape.common import PromptStack


class TestStartPromptEvent:
    @pytest.fixture
    def start_prompt_event(self):
        prompt_stack = PromptStack()
        prompt_stack.add_user_input("foo")
        prompt_stack.add_system_input("bar")
        return StartPromptEvent(token_count=123, prompt_stack=prompt_stack, prompt="foo bar", model="foo bar")

    def test_to_dict(self, start_prompt_event):
        assert "timestamp" in start_prompt_event.to_dict()

        assert start_prompt_event.to_dict()["token_count"] == 123
        assert start_prompt_event.to_dict()["prompt_stack"]["inputs"][0]["content"] == "foo"
        assert start_prompt_event.to_dict()["prompt_stack"]["inputs"][0]["role"] == "user"
        assert start_prompt_event.to_dict()["prompt_stack"]["inputs"][1]["content"] == "bar"
        assert start_prompt_event.to_dict()["prompt_stack"]["inputs"][1]["role"] == "system"

        assert start_prompt_event.to_dict()["prompt"] == "foo bar"
        assert start_prompt_event.to_dict()["model"] == "foo bar"
