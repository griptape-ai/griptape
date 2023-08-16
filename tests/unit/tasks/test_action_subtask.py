import json
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.structures import Pipeline


class TestActionSubtask:
    def test_to_json(self):
        valid_input = 'Thought: need to test\n' \
                      'Action: {"type": "tool", "name": "test", "activity": "test action", "input": "test input"}\n' \
                      'Observation: test observation\n' \
                      'Answer: test output'

        task = ToolkitTask(tools=[])
        Pipeline().add_task(task)
        subtask = task.add_subtask(ActionSubtask(valid_input))
        json_dict = json.loads(subtask.action_to_json())

        assert json_dict["type"] == "tool"
        assert json_dict["name"] == "test"
        assert json_dict["activity"] == "test action"
        assert json_dict["input"] == "test input"

    def test_input(self):
        assert ActionSubtask("{{ hello }}").input.value == "{{ hello }}"

    def test___remove_null_values_in_dict_recursively(self):
        dict_with_nones = {
            "foo": None,
            "bar": {
                "baz": {
                    "foo": [1, 2, 3],
                    "bar": None
                }
            }
        }

        dict_without_nones = {
            "bar": {
                "baz": {
                    "foo": [1, 2, 3]
                }
            }
        }

        assert ActionSubtask().remove_null_values_in_dict_recursively(dict_with_nones) == dict_without_nones
