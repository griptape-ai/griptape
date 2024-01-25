import json
from tests.mocks.mock_tool.tool import MockTool
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.structures import Agent


class TestActionSubtask:
    def test_to_json(self):
        valid_input = (
            "Thought: need to test\n"
            'Action: {"name": "MockTool", "path": "test", "input": {"values": {"test": "value"}}}\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.action_to_json())

        assert json_dict["name"] == "MockTool"
        assert json_dict["path"] == "test"
        assert json_dict["input"] == {"values": {"test": "value"}}

    def test_init_from_action_with_newlines(self):
        valid_input = (
            "Thought: need to test\n"
            'Action:\nFoobarfoobar baz}!@#$%^&*()123(*!378934)\n\n```json\n{"name": "MockTool",\n"path": "test",\n\n"input": {"values":\n{"test":\n"test\n\ninput\n\nwith\nnewlines"}}}```!@#$%^&*()123(*!378934)'
            "Response: test response\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.action_to_json())

        assert json_dict["name"] == "MockTool"
        assert json_dict["path"] == "test"
        assert json_dict["input"] == {"values": {"test": "test\n\ninput\n\nwith\nnewlines"}}

    def test_input(self):
        assert ActionSubtask("{{ hello }}").input.value == "{{ hello }}"
