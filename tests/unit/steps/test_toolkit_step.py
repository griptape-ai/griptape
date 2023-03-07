from warpspeed.steps import ToolkitStep
from warpspeed.tools import PingPongTool, CalculatorTool
from tests.mocks.mock_value_driver import MockValueDriver
from warpspeed.structures import Pipeline


class TestToolkitStep:
    def test_run(self):
        output = """Action: {"tool": "exit", "input": "test is finished"}"""

        step = ToolkitStep("test", tools=[PingPongTool(), CalculatorTool()])
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step.tools) == 2
        assert len(step.substeps) == 1
        assert step.substeps[0].action_name == "exit"
        assert step.substeps[0].action_input == "test is finished"
        assert result.output.value == "test is finished"

    def test_find_tool(self):
        tool = PingPongTool()
        step = ToolkitStep("test", tools=[PingPongTool()])

        assert step.find_tool(tool.name) == tool
        