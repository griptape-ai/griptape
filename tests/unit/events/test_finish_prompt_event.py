import pytest
from griptape.events import FinishPromptEvent

class TestFinishPromptEvent:
    @pytest.fixture
    def finish_prompt_event(self):
        return FinishPromptEvent()
