import pytest
from warpspeed.tools import WebScraperTool


class TestWebScraperTool:
    URL = "https://github.com/usewarpspeed/warpspeed"

    @pytest.fixture
    def tool(self):
        return WebScraperTool()

    def test_run_title(self, tool):
        result = tool.run({
            "url": self.URL,
            "action": "title"
        })

        assert isinstance(result, str)

    def test_run_author(self, tool):
        result = tool.run({
            "url": self.URL,
            "action": "author"
        })

        assert isinstance(result, str)

    def test_run_full_text(self, tool):
        result = tool.run({
            "url": self.URL,
            "action": "full_text"
        })

        assert isinstance(result, str)

    def test_run_summary(self, tool):
        result = tool.run({
            "url": self.URL,
            "action": "summary"
        })

        assert isinstance(result, str)

    def test_run_keywords(self, tool):
        result = tool.run({
            "url": self.URL,
            "action": "keywords"
        })

        assert isinstance(result, str)
