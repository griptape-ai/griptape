import json
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.structures import Pipeline


class TestActionSubtask:
    def test_to_json(self):
        valid_input = (
            "Thought: need to test\n"
            'Request: {"type": "tool", "name": "test", "path": "test action", "input": "test input"}\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[])
        Pipeline().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.request_to_json())

        assert json_dict["name"] == "test"
        assert json_dict["path"] == "test action"
        assert json_dict["input"] == "test input"

    def test_init_from_request_with_newlines(self):
        valid_input = (
            "Thought: need to test\n"
            'Request:\nFoobarfoobar baz}!@#$%^&*()123(*!378934)\n\n```json\n{"type":\n "tool",\n\n"name": "test",\n"path": \n"test action", \n"input": "test\n\ninput\n\nwith\nnewlines"}\n\nFoobizbar1)(*&^%$#@!)'
            "Response: test response\n"
            "Answer: test output"
        )

        task = ToolkitTask(tools=[])
        Pipeline().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.request_to_json())

        assert json_dict["name"] == "test"
        assert json_dict["path"] == "test action"
        assert json_dict["input"] == "test\n\ninput\n\nwith\nnewlines"

    def test_input(self):
        assert ActionSubtask("{{ hello }}").input.value == "{{ hello }}"
