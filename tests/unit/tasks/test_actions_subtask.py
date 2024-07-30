import json

from griptape.artifacts import ActionArtifact, ListArtifact, TextArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.common import ToolAction
from griptape.structures import Agent
from griptape.tasks import ActionsSubtask, ToolkitTask
from tests.mocks.mock_tool.tool import MockTool


class TestActionsSubtask:
    def test_basic_input(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions: [{"tag": "foo", "name": "MockTool", "path": "test", "input": {"values": {"test": "value"}}}]\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test"
        assert json_dict[0]["input"] == {"values": {"test": "value"}}

    def test_action_input(self):
        valid_input = ActionArtifact(
            ToolAction(tag="foo", name="MockTool", path="test", input={"values": {"test": "value"}})
        )
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert subtask.thought is None
        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test"
        assert json_dict[0]["input"] == {"values": {"test": "value"}}

    def test_action_and_thought_input(self):
        valid_input = ListArtifact(
            [
                TextArtifact("thought"),
                ActionArtifact(
                    ToolAction(tag="foo", name="MockTool", path="test", input={"values": {"test": "value"}})
                ),
            ]
        )
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert subtask.thought == "thought"
        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test"
        assert json_dict[0]["input"] == {"values": {"test": "value"}}

    def test_callable_input(self):
        valid_input = ListArtifact(
            [
                TextArtifact("thought"),
                ActionArtifact(
                    ToolAction(tag="foo", name="MockTool", path="test", input={"values": {"test": "value"}})
                ),
            ]
        )
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(lambda task: valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert subtask.thought == "thought"
        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test"
        assert json_dict[0]["input"] == {"values": {"test": "value"}}

    def test_input_with_multiline_actions(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions:\nFoobarfoobar baz}!@#$%^&*()123(*!378934)\n\n```json\n[{"tag": "foo", "name": "MockTool",\n"path": "test",\n\n"input": {"values":\n{"test":\n"test\n\ninput\n\nwith\nnewlines"}}}]```!@#$%^&*()123(*!378934)'
            "Response: test response\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test"
        assert json_dict[0]["input"] == {"values": {"test": "test\n\ninput\n\nwith\nnewlines"}}

    def test_input(self):
        assert ActionsSubtask("{{ hello }}").input.value == "{{ hello }}"

    def test_with_no_action_input(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions: [{"tag": "foo", "name": "MockTool", "path": "test_no_schema"}]\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test_no_schema"
        assert json_dict[0].get("input") is None

    def test_no_actions(self):
        valid_input = "Thought: need to test\n" "<|Response|>: test observation\n" "Answer: test output"

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert len(json_dict) == 0

    def test_empty_actions(self):
        valid_input = "Thought: need to test\n" "Actions: []\n" "<|Response|>: test observation\n" "Answer: test output"

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert len(json_dict) == 0

    def test_invalid_actions(self):
        invalid_input = (
            "Thought: need to test\n" "Actions: [{,{]\n" "<|Response|>: test observation\n" "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(invalid_input))

        assert isinstance(subtask.output, ErrorArtifact)
        assert "Actions JSON decoding error" in subtask.output.value

    def test_implicit_values(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions:[{"tag": "foo", "name": "MockTool","path": "test","input": {"test":\n"value"}}]'
            "Response: test response\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        json_dict = json.loads(subtask.actions_to_json())

        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test"
        assert json_dict[0]["input"] == {"values": {"test": "value"}}

    def test_execute_tool(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions:[{"tag": "foo", "name": "MockTool","path": "test","input": {"values": {"test": "value"}}}]'
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        subtask.execute()

        assert isinstance(subtask.output, ListArtifact)
        assert isinstance(subtask.output.value[0], TextArtifact)
        assert subtask.output.value[0].value == "ack value"

    def test_execute_tool_exception(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions:[{"tag": "foo", "name": "MockTool","path": "test_exception","input": {"values": {"test": "value"}}}]'
        )

        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(valid_input))
        subtask.execute()

        assert isinstance(subtask.output, ListArtifact)
        assert isinstance(subtask.output.value[0], ErrorArtifact)
        assert subtask.output.value[0].value == "error value"
