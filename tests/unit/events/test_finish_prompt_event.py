import pytest
from griptape.events import FinishPromptEvent


class TestFinishPromptEvent:
    @pytest.fixture
    def finish_prompt_event(self):
        return FinishPromptEvent(token_count=123)

    def test_token_count(self, finish_prompt_event):
        assert finish_prompt_event.token_count == 123

    def test_to_dict(self, finish_prompt_event):
        assert "timestamp" in finish_prompt_event.to_dict()
        assert finish_prompt_event.to_dict()["token_count"] == 123
