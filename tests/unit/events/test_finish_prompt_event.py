import pytest
from griptape.events import FinishPromptEvent


class TestFinishPromptEvent:
    @pytest.fixture
    def finish_prompt_event(self):
        return FinishPromptEvent(token_count=123, result="foo bar", model="foo bar")

    def test_to_dict(self, finish_prompt_event):
        assert "timestamp" in finish_prompt_event.to_dict()

        assert finish_prompt_event.to_dict()["token_count"] == 123

        assert finish_prompt_event.to_dict()["result"] == "foo bar"
        assert finish_prompt_event.to_dict()["model"] == "foo bar"
