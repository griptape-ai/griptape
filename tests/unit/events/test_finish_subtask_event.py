import pytest
from griptape.events import FinishSubtaskEvent
from griptape.tasks import ActionSubtask


class TestFinishSubtaskEvent:
    @pytest.fixture
    def finish_subtask_event(self):
        return FinishSubtaskEvent(subtask=ActionSubtask())

    def test_subtask(self, finish_subtask_event):
        assert isinstance(finish_subtask_event.subtask, ActionSubtask)
