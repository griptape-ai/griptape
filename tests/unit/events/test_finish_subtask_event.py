import pytest
from griptape.events import FinishSubtaskEvent
from griptape.tasks import ApiRequestSubtask


class TestFinishSubtaskEvent:
    @pytest.fixture
    def finish_subtask_event(self):
        return FinishSubtaskEvent(subtask=ApiRequestSubtask())

    def test_subtask(self, finish_subtask_event):
        assert isinstance(finish_subtask_event.subtask, ApiRequestSubtask)
