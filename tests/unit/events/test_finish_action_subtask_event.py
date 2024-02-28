import pytest
from griptape.events import FinishActionSubtaskEvent
from griptape.structures import Agent
from griptape.tasks import ActionSubtask, ToolkitTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestFinishActionSubtaskEvent:
    @pytest.fixture
    def finish_subtask_event(self):
        valid_input = (
            "Thought: need to test\n"
            'Action: {"name": "test", "path": "test action", "input": {"values": {"foo": "test input"}}}\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )
        task = ToolkitTask()
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)
        subtask = ActionSubtask(valid_input)
        task.add_subtask(subtask)
        agent.run()

        return FinishActionSubtaskEvent(
            task_id=subtask.id,
            task_parent_ids=subtask.parent_ids,
            task_child_ids=subtask.child_ids,
            task_input=subtask.input,
            task_output=subtask.output,
            subtask_parent_task_id=subtask.parent_task_id,
            subtask_thought=subtask.thought,
            subtask_action_name=subtask.action_name,
            subtask_action_path=subtask.action_path,
            subtask_action_input=subtask.action_input,
        )

    def test_to_dict(self, finish_subtask_event):
        event_dict = finish_subtask_event.to_dict()

        assert "timestamp" in event_dict
        assert event_dict["task_id"] == finish_subtask_event.task_id
        assert event_dict["task_parent_ids"] == finish_subtask_event.task_parent_ids
        assert event_dict["task_child_ids"] == finish_subtask_event.task_child_ids
        assert event_dict["task_input"] == finish_subtask_event.task_input.to_dict()
        assert event_dict["task_output"] is None

        assert event_dict["subtask_parent_task_id"] == finish_subtask_event.subtask_parent_task_id
        assert event_dict["subtask_thought"] == finish_subtask_event.subtask_thought
        assert event_dict["subtask_action_name"] == finish_subtask_event.subtask_action_name
        assert event_dict["subtask_action_path"] == finish_subtask_event.subtask_action_path
        assert event_dict["subtask_action_input"] == finish_subtask_event.subtask_action_input
