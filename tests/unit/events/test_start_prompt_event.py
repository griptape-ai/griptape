import pytest

from griptape.common import PromptStack
from griptape.events import StartPromptEvent


class TestStartPromptEvent:
    @pytest.fixture()
    def start_prompt_event(self):
        prompt_stack = PromptStack()
        prompt_stack.add_user_message("foo")
        prompt_stack.add_system_message("bar")
        return StartPromptEvent(prompt_stack=prompt_stack, model="foo bar")

    def test_to_dict(self, start_prompt_event):
        assert "timestamp" in start_prompt_event.to_dict()

        assert start_prompt_event.to_dict()["prompt_stack"]["messages"][0]["content"][0]["artifact"]["value"] == "foo"
        assert start_prompt_event.to_dict()["prompt_stack"]["messages"][0]["role"] == "user"
        assert start_prompt_event.to_dict()["prompt_stack"]["messages"][1]["content"][0]["artifact"]["value"] == "bar"
        assert start_prompt_event.to_dict()["prompt_stack"]["messages"][1]["role"] == "system"

        assert start_prompt_event.to_dict()["model"] == "foo bar"
