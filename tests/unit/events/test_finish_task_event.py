import pytest
from griptape.structures import Agent
from griptape.events import FinishTaskEvent
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestFinishTaskEvent:
    @pytest.fixture
    def finish_task_event(self):
        task = PromptTask()
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)
        agent.run()

        return FinishTaskEvent.from_task(task)

    def test_to_dict(self, finish_task_event):
        event_dict = finish_task_event.to_dict()

        assert "timestamp" in event_dict
        assert event_dict["task_id"] == finish_task_event.task_id
        assert event_dict["task_parent_ids"] == finish_task_event.task_parent_ids
        assert event_dict["task_child_ids"] == finish_task_event.task_child_ids
        assert event_dict["task_input"] == finish_task_event.task_input.to_dict()
        assert event_dict["task_output"] == finish_task_event.task_output.to_dict()
