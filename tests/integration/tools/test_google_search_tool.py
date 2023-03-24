import pytest
from warpspeed.tools.google_search.google_search_tool import GoogleSearchTool


class TestGoogleSearchTool:
    QUERY = "LLM models"

    @pytest.fixture
    def tool(self):
        return GoogleSearchTool()

    def test_run(self, tool):
        result = tool.run(self.QUERY)

        assert isinstance(result, str)
