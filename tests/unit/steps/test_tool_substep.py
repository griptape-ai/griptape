import json
from griptape.tasks import ToolkitTask, ToolStep
from griptape.structures import Pipeline


class TestToolSubstep:
    def test_to_json(self):
        valid_input = """Thought: need to test\nAction: {"tool": "test", "action": "test action", "value": "test input"}\nObservation: test 
        observation\nOutput: test output"""

        task = ToolkitTask(tool_names=[])
        Pipeline().add_task(task)
        substep = task.add_step(ToolStep(valid_input))
        json_dict = json.loads(substep.to_json())

        assert json_dict["tool"] == "test"
        assert json_dict["action"] == "test action"
        assert json_dict["value"] == "test input"
