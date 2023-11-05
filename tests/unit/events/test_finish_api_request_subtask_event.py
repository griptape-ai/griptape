import pytest
from griptape.events import FinishApiRequestSubtaskEvent
from griptape.structures import Agent
from griptape.tasks import ApiRequestSubtask, ToolkitTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestFinishApiRequestSubtaskEvent:
    @pytest.fixture
    def finish_subtask_event(self):
        valid_input = (
            "Thought: need to test\n"
            'Request: {"name": "test", "path": "test action", "input": {"values": {"foo": "test input"}}}\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )
        task = ToolkitTask()
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)
        subtask = ApiRequestSubtask(valid_input)
        task.add_subtask(subtask)
        agent.run()

        return FinishApiRequestSubtaskEvent.from_task(subtask)

    def test_to_dict(self, finish_subtask_event):
        event_dict = finish_subtask_event.to_dict()

        assert "timestamp" in event_dict
        assert event_dict["task_id"] == finish_subtask_event.task_id
        assert (
            event_dict["task_parent_ids"]
            == finish_subtask_event.task_parent_ids
        )
        assert (
            event_dict["task_child_ids"] == finish_subtask_event.task_child_ids
        )
        assert (
            event_dict["task_input"]
            == finish_subtask_event.task_input.to_dict()
        )
        assert event_dict["task_output"] is None

        assert (
            event_dict["subtask_parent_task_id"]
            == finish_subtask_event.subtask_parent_task_id
        )
        assert (
            event_dict["subtask_thought"]
            == finish_subtask_event.subtask_thought
        )
        assert (
            event_dict["subtask_api_name"]
            == finish_subtask_event.subtask_api_name
        )
        assert (
            event_dict["subtask_api_path"]
            == finish_subtask_event.subtask_api_path
        )
        assert (
            event_dict["subtask_api_input"]
            == finish_subtask_event.subtask_api_input
        )
