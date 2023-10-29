import pytest
from griptape.events import StartSubtaskEvent
from griptape.tasks import ApiRequestSubtask


class TestStartSubtaskEvent:
    @pytest.fixture
    def start_subtask_event(self):
        return StartSubtaskEvent(subtask=ApiRequestSubtask())

    def test_subtask(self, start_subtask_event):
        assert isinstance(start_subtask_event.subtask, ApiRequestSubtask)
