import json
from griptape.tasks import ToolkitTask, ToolSubtask
from griptape.structures import Pipeline


class TestToolSubsubtask:
    def test_to_json(self):
        valid_input = 'Thought: need to test\n' \
                      'Action: {"type": "tool", "name": "test", "method": "test action", "input": "test input"}\n' \
                      'Observation: test observation\n' \
                      'Output: test output'

        task = ToolkitTask(tool_names=[])
        Pipeline().add_task(task)
        subsubtask = task.add_subtask(ToolSubtask(valid_input))
        json_dict = json.loads(subsubtask.to_json())

        assert json_dict["type"] == "tool"
        assert json_dict["name"] == "test"
        assert json_dict["method"] == "test action"
        assert json_dict["input"] == "test input"
