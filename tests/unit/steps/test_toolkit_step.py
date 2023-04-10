from skatepark.steps import ToolkitStep
from tests.mocks.mock_value_driver import MockValueDriver
from skatepark.structures import Pipeline


class TestToolkitStep:
    def test_run(self):
        output = """Output: done"""

        tools = [
            "calculator",
            "google_search"
        ]

        step = ToolkitStep("test", tool_names=tools)
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step.tools) == 2
        assert len(step._substeps) == 1
        assert result.output.value == "done"

    def test_find_tool(self):
        tool = "calculator"
        step = ToolkitStep("test", tool_names=["calculator"])

        assert step.find_tool(tool.name) == tool
        