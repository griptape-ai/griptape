from griptape.tools import Calculator, WebSearch
from skatepark.steps import ToolkitStep
from skatepark.utils import ToolLoader
from tests.mocks.mock_value_driver import MockValueDriver
from skatepark.structures import Pipeline


class TestToolkitStep:
    def test_run(self):
        output = """Output: done"""

        tools = [
            Calculator(),
            WebSearch()
        ]

        step = ToolkitStep("test", tool_names=["Calculator", "WebSearch"])
        pipeline = Pipeline(
            prompt_driver=MockValueDriver(output),
            tool_loader=ToolLoader(tools=tools)
        )

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step.tools) == 2
        assert len(step._substeps) == 1
        assert result.output.value == "done"

    def test_find_tool(self):
        tool = Calculator()
        step = ToolkitStep("test", tool_names=[tool.name])

        Pipeline(
            tool_loader=ToolLoader(tools=[tool])
        ).add_step(step)

        assert step.find_tool(tool.name) == tool
