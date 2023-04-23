from griptape.tools import Calculator, WebScraper
from griptape.utils import ToolLoader


class TestToolLoader:
    def test_init(self):
        loader = ToolLoader(tools=[Calculator(), WebScraper()])

        assert len(loader.tools) == 2

        try:
            ToolLoader(tools=[Calculator(), Calculator()])
        except ValueError:
            assert True

    def test_load_tool(self):
        loader = ToolLoader(tools=[Calculator(name="MyCalculator"), WebScraper()])

        assert isinstance(loader.load_tool("MyCalculator"), Calculator)