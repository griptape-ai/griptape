import pytest
from griptape.events import FinishTaskEvent
from griptape.tasks import PromptTask


class TestFinishTaskEvent:
    @pytest.fixture
    def finish_task_event(self):
        return FinishTaskEvent(task=PromptTask())

    def test_task(self, finish_task_event):
        assert isinstance(finish_task_event.task, PromptTask)
