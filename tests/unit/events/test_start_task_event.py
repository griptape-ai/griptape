import pytest
from griptape.events import StartTaskEvent
from griptape.tasks import PromptTask


class TestStartTaskEvent:
    @pytest.fixture
    def start_task_event(self):
        return StartTaskEvent(task=PromptTask())

    def test_task(self, start_task_event):
        assert isinstance(start_task_event.task, PromptTask)

    def test_to_dict(self, start_task_event):
        event_dict = start_task_event.to_dict()
        del event_dict["task"]["type"]  # remove extra field from PolymorphicSchema

        assert "timestamp" in event_dict
        assert event_dict["task"] == start_task_event.task.to_dict()
