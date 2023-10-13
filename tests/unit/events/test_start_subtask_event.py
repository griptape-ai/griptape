import pytest
from griptape.events import StartSubtaskEvent
from griptape.tasks import ActionSubtask

class TestStartSubtaskEvent:
    @pytest.fixture
    def start_subtask_event(self):
        return StartSubtaskEvent(subtask=ActionSubtask())

    def test_subtask(self, start_subtask_event):
        assert isinstance(start_subtask_event.subtask, ActionSubtask)

    def test_to_dict(self, start_subtask_event):
        assert 'timestamp' in start_subtask_event.to_dict()
        assert start_subtask_event.to_dict()['subtask'] == start_subtask_event.subtask.to_dict()
