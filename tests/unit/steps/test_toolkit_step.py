from warpspeed.steps import ToolkitStep
from warpspeed.tools import PingPongTool, CalculatorTool
from tests.mocks.mock_value_driver import MockValueDriver
from warpspeed.structures import Pipeline


class TestToolkitStep:
    def test_run(self):
        output = """Output: done"""

        step = ToolkitStep("test", tools=[PingPongTool(), CalculatorTool()])
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step.tools) == 2
        assert len(step._substeps) == 1
        assert result.output.value == "done"

    def test_find_tool(self):
        tool = PingPongTool()
        step = ToolkitStep("test", tools=[PingPongTool()])

        assert step.find_tool(tool.name) == tool
        