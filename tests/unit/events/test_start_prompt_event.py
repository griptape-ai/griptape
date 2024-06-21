import pytest
from griptape.events import StartPromptEvent
from griptape.common import MessageStack


class TestStartPromptEvent:
    @pytest.fixture
    def start_prompt_event(self):
        message_stack = MessageStack()
        message_stack.add_user_message("foo")
        message_stack.add_system_message("bar")
        return StartPromptEvent(message_stack=message_stack, model="foo bar")

    def test_to_dict(self, start_prompt_event):
        assert "timestamp" in start_prompt_event.to_dict()

        assert start_prompt_event.to_dict()["message_stack"]["messages"][0]["content"][0]["artifact"]["value"] == "foo"
        assert start_prompt_event.to_dict()["message_stack"]["messages"][0]["role"] == "user"
        assert start_prompt_event.to_dict()["message_stack"]["messages"][1]["content"][0]["artifact"]["value"] == "bar"
        assert start_prompt_event.to_dict()["message_stack"]["messages"][1]["role"] == "system"

        assert start_prompt_event.to_dict()["model"] == "foo bar"
