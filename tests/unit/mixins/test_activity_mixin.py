import pytest
from schema import Schema, Literal
from tests.mocks.mock_tool.tool import MockTool


class TestActivityMixin:
    @pytest.fixture
    def tool(self):
        return MockTool(test_field="hello", test_int=5)

    def test_activity_name(self, tool):
        assert tool.activity_name(tool.test) == "test"

    def test_activity_description(self, tool):
        description = tool.activity_description(tool.test)

        assert description == f"test description: {tool.foo()}"

    def test_activity_schema(self, tool):
        schema = tool.activity_schema(tool.test)

        assert schema == Schema({"values": tool.test.config["schema"].schema}).json_schema("InputSchema")
        assert schema["properties"].get("artifact") is None

    def test_activity_with_no_schema(self, tool):
        assert tool.activity_schema(tool.test_no_schema) is None

    def test_find_activity(self):
        tool = MockTool(test_field="hello", test_int=5, allowlist=["test"])
        assert tool.find_activity("test") == tool.test
        assert tool.find_activity("test_str_output") is None

    def test_activities(self, tool):
        assert len(tool.activities()) == 6
        assert tool.activities()[0] == tool.test

    def test_allowlist_and_denylist_validation(self):
        with pytest.raises(ValueError):
            MockTool(test_field="hello", test_int=5, allowlist=[], denylist=[])

    def test_allowlist(self):
        tool = MockTool(test_field="hello", test_int=5, allowlist=["test"])

        assert len(tool.activities()) == 1

    def test_denylist(self):
        tool = MockTool(test_field="hello", test_int=5, denylist=["test"])

        assert len(tool.activities()) == 5

    def test_invalid_allowlist(self):
        with pytest.raises(ValueError):
            MockTool(test_field="hello", test_int=5, allowlist=["test_foo"])

    def test_invalid_denylist(self):
        with pytest.raises(ValueError):
            MockTool(test_field="hello", test_int=5, denylist=["test_foo"])

    def test_disable_activities(self, tool):
        assert len(tool.activities()) > 0

        tool.disable_activities()

        assert len(tool.activities()) == 0

    def test_enable_activities(self, tool):
        tool.disable_activities()

        assert len(tool.activities()) == 0

        tool.enable_activities()

        assert len(tool.activities()) > 0

    def test_activity_to_input(self, tool):
        input = tool.activity_to_input(tool.test)
        assert str(input) == str(
            {Literal("input", description=""): {"values": Schema({Literal("test"): str}, description="Test input")}}
        )

        input = tool.activity_to_input(tool.test_no_schema)
        assert input == {}
