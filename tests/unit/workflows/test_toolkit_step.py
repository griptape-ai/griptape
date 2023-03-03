from galaxybrain.workflows import Workflow, ToolkitStep
from galaxybrain.tools import PingPongTool, CalculatorTool
from tests.mocks.mock_value_driver import MockValueDriver


class TestToolkitStep:
    def test_run(self):
        output = """Action: {"tool": "exit", "input": "test is finished"}"""

        step = ToolkitStep("test", tools=[PingPongTool(), CalculatorTool()])
        workflow = Workflow(prompt_driver=MockValueDriver(output))

        workflow.add_step(step)

        result = workflow.start()

        assert len(step.tools) == 2
        assert len(step.substeps) == 1
        assert step.substeps[0].action_name == "exit"
        assert step.substeps[0].action_input == "test is finished"
        assert result.value == "test is finished"
