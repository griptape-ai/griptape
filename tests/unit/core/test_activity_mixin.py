import pytest
from tests.mocks.mock_tool.tool import MockTool


class TestActivityMixin:
    @pytest.fixture
    def tool(self):
        return MockTool(
            test_field="hello",
            test_int=5
        )

    def test_activity_name(self, tool):
        assert tool.activity_name(tool.test) == "test"

    def test_activity_description(self, tool):
        description = tool.activity_description(tool.test)

        assert "bar" in description
        assert "baz" not in description

    def test_full_activity_description(self, tool):
        description = tool.full_activity_description(tool.test)

        assert "bar" in description
        assert "baz" not in description

    def test_activity_schema(self, tool):
        assert tool.activity_schema(tool.test) == \
               tool.test.config["schema"].json_schema("ToolInputSchema")

    def test_find_activity(self, tool):
        assert tool.find_activity("test") == tool.test

    def test_activities(self, tool):
        assert len(tool.activities()) == 3
        assert tool.activities()[0] == tool.test
