import json
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.structures import Pipeline


class TestActionSubtask:
    def test_to_json(self):
        valid_input = (
            "Thought: need to test\n"
            'Action: {"type": "tool", "name": "test", "activity": "test action", "input": "test input"}\n'
            "Observation: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[])
        Pipeline().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.action_to_json())

        assert json_dict["type"] == "tool"
        assert json_dict["name"] == "test"
        assert json_dict["activity"] == "test action"
        assert json_dict["input"] == "test input"

    def test_to_dict(self):
        valid_input = (
            "Thought: need to test\n"
            'Action: {"type": "tool", "name": "test", "activity": "test action", "input": "test input"}\n'
            "Observation: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[])
        Pipeline().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))

        assert subtask.to_dict() == {
            "id": subtask.id,
            "state": 1,
            "parent_ids": [],
            "child_ids": [],
            "output": None,
            "input": {
                "id": subtask.input.id,
                "name": subtask.input.name,
                "type": "TextArtifact",
                "value": valid_input,
            },
            "input_template": valid_input,
            "context": {},
            "parent_task_id": task.id,
            "thought": "need to test",
            "action_type": "tool",
            "action_name": "test",
            "action_activity": "test action",
            "action_input": "test input",
        }

    def test_init_from_action_with_newlines(self):
        valid_input = (
            "Thought: need to test\n"
            'Action:\nFoobarfoobar baz}!@#$%^&*()123(*!378934)\n\n```json\n{"type":\n "tool",\n\n"name": "test",\n"activity": \n"test action", \n"input": "test\n\ninput\n\nwith\nnewlines"}\n\nFoobizbar1)(*&^%$#@!)'
            "Observation: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[])
        Pipeline().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.action_to_json())

        assert json_dict["type"] == "tool"
        assert json_dict["name"] == "test"
        assert json_dict["activity"] == "test action"
        assert json_dict["input"] == "test\n\ninput\n\nwith\nnewlines"

    def test_input(self):
        assert ActionSubtask("{{ hello }}").input.value == "{{ hello }}"
