import pytest

from griptape.events import FinishActionsSubtaskEvent
from griptape.structures import Agent
from griptape.tasks import ActionsSubtask, ToolkitTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestFinishActionsSubtaskEvent:
    @pytest.fixture()
    def finish_subtask_event(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions: [{"tag": "foo", "name": "MockTool", "path": "test", "input": {"values": {"test": "test input"}}}]\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )
        task = ToolkitTask(tools=[MockTool()])
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)
        subtask = ActionsSubtask(valid_input)
        task.add_subtask(subtask)
        agent.run()

        return FinishActionsSubtaskEvent(
            task_id=subtask.id,
            task_parent_ids=subtask.parent_ids,
            task_child_ids=subtask.child_ids,
            task_input=subtask.input,
            task_output=subtask.output,
            subtask_parent_task_id=subtask.parent_task_id,
            subtask_thought=subtask.thought,
            subtask_actions=subtask.actions_to_dicts(),
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
        assert event_dict["subtask_actions"][0]["tag"] == finish_subtask_event.subtask_actions[0]["tag"]
        assert event_dict["subtask_actions"][0]["name"] == finish_subtask_event.subtask_actions[0]["name"]
        assert event_dict["subtask_actions"][0]["path"] == finish_subtask_event.subtask_actions[0]["path"]
        assert event_dict["subtask_actions"][0]["input"] == finish_subtask_event.subtask_actions[0]["input"]
