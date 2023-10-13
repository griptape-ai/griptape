import pytest
from griptape.events import FinishTaskEvent
from griptape.tasks import PromptTask


class TestFinishTaskEvent:
    @pytest.fixture
    def finish_task_event(self):
        return FinishTaskEvent(task=PromptTask())

    def test_task(self, finish_task_event):
        assert isinstance(finish_task_event.task, PromptTask)

    def test_to_dict(self, finish_task_event):
        event_dict = finish_task_event.to_dict()
        del event_dict["task"]["type"]  # remove extra field from PolymorphicSchema

        assert "timestamp" in event_dict
        assert event_dict["task"] == finish_task_event.task.to_dict()
