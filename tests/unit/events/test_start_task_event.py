import pytest
from griptape.events import StartTaskEvent
from griptape.tasks import PromptTask


class TestStartTaskEvent:
    @pytest.fixture
    def start_task_event(self):
        return StartTaskEvent(task=PromptTask())

    def test_task(self, start_task_event):
        assert isinstance(start_task_event.task, PromptTask)
