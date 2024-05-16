import json
import pytest
from griptape.artifacts.actions_artifact import ActionsArtifact
from tests.mocks.mock_tool.tool import MockTool
from griptape.tasks import ToolkitTask, ActionsSubtask
from griptape.structures import Agent


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

        assert (
            ActionsSubtask(
                ActionsArtifact(
                    value="foo bar",
                    actions=[
                        ActionsArtifact.Action(tag="foo", name="bar", path="baz", input={}),
                        ActionsArtifact.Action(tag="baz", name="foo", path="bar", input={}),
                    ],
                )
            ).input.value
            == "foo bar"
        )

    @pytest.mark.parametrize(
        "input",
        [
            (
                "Thought: need to test\n"
                'Actions: [{"tag": "foo", "name": "MockTool", "path": "test_no_schema"}]\n'
                "<|Response|>: test observation\n"
                "Answer: test output"
            ),
            ActionsArtifact(
                value="foo bar", actions=[ActionsArtifact.Action(tag="foo", name="MockTool", path="test_no_schema")]
            ),
        ],
    )
    def test_with_no_action_input(self, input):
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(input))
        json_dict = json.loads(subtask.actions_to_json())

        assert json_dict[0]["name"] == "MockTool"
        assert json_dict[0]["path"] == "test_no_schema"
        assert json_dict[0].get("input") is None

    @pytest.mark.parametrize(
        "input",
        [
            "Thought: need to test\n" "<|Response|>: test observation\n" "Answer: test output",
            ActionsArtifact(value="foo bar"),
        ],
    )
    def test_no_actions(self, input):
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(input))
        json_dict = json.loads(subtask.actions_to_json())

        assert len(json_dict) == 0

    @pytest.mark.parametrize(
        "input",
        [
            "Thought: need to test\n" "Actions: []\n" "<|Response|>: test observation\n" "Answer: test output",
            ActionsArtifact(value="foo bar", actions=[]),
        ],
    )
    def test_empty_actions(self, input):
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(input))
        json_dict = json.loads(subtask.actions_to_json())

        assert len(json_dict) == 0

    @pytest.mark.parametrize(
        "input", ["Thought: need to test\n" "Actions: [{,{]\n" "<|Response|>: test observation\n" "Answer: test output"]
    )
    def test_invalid_actions(self, input):
        task = ToolkitTask(tools=[MockTool()])
        Agent().add_task(task)
        subtask = task.add_subtask(ActionsSubtask(input))
        json_dict = json.loads(subtask.actions_to_json())

        assert json_dict[0]["name"] == "error"
        assert "Action input parsing error" in json_dict[0]["input"]["error"]
