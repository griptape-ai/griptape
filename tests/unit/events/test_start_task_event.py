import pytest
from griptape.events import StartTaskEvent
from griptape.structures import Agent
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestStartTaskEvent:
    @pytest.fixture
    def start_task_event(self):
        task = PromptTask()
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)
        agent.run()

        return StartTaskEvent(
            task_id=task.id,
            task_parent_ids=task.parent_ids,
            task_child_ids=task.child_ids,
            task_input=task.input,
            task_output=task.output,
        )

    def test_to_dict(self, start_task_event):
        event_dict = start_task_event.to_dict()

        assert "timestamp" in event_dict
        assert event_dict["task_id"] == start_task_event.task_id
        assert event_dict["task_parent_ids"] == start_task_event.task_parent_ids
        assert event_dict["task_child_ids"] == start_task_event.task_child_ids
        assert event_dict["task_input"] == start_task_event.task_input.to_dict()
        assert event_dict["task_output"] == start_task_event.task_output.to_dict()
