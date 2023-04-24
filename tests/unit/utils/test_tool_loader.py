from tests.mocks.mock_tool.tool import MockTool
from griptape.utils import ToolLoader


class TestToolLoader:
    def test_init(self):
        loader = ToolLoader(tools=[MockTool(name="ToolOne"), MockTool(name="ToolTwo")])

        assert len(loader.tools) == 2

        try:
            ToolLoader(tools=[MockTool(), MockTool()])
        except ValueError:
            assert True

    def test_load_tool(self):
        loader = ToolLoader(tools=[MockTool(name="MyCalculator"), MockTool()])

        assert isinstance(loader.load_tool("MyCalculator"), MockTool)