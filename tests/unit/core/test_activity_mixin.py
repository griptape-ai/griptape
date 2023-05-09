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
        schema = tool.activity_schema(tool.test)
        assert schema == \
               tool.test.config["schema"].json_schema("InputSchema")

        assert schema["properties"].get("artifact") is None

    def test_activity_schema_with_ramp(self, tool):
        props = tool.activity_schema(tool.test_with_required_ramp)["properties"]

        assert props["test"]
        assert isinstance(props["records"], dict)

    def test_activity_with_no_schema(self, tool):
        assert tool.activity_schema(tool.test_no_schema) is None

    def test_find_activity(self):
        tool = MockTool(
            test_field="hello",
            test_int=5,
            allowlist=["test"]
        )
        assert tool.find_activity("test") == tool.test
        assert tool.find_activity("test_str_output") is None

    def test_activities(self, tool):
        assert len(tool.activities()) == 5
        assert tool.activities()[0] == tool.test

    def test_allowlist_and_denylist_validation(self):
        with pytest.raises(ValueError):
            MockTool(
                test_field="hello",
                test_int=5,
                allowlist=[],
                denylist=[]
            )

    def test_allowlist(self):
        tool = MockTool(
            test_field="hello",
            test_int=5,
            allowlist=["test"]
        )

        assert len(tool.activities()) == 1

    def test_denylist(self):
        tool = MockTool(
            test_field="hello",
            test_int=5,
            denylist=["test"]
        )

        assert len(tool.activities()) == 4

    def test_should_pass_artifacts(self, tool):
        assert tool.should_pass_artifacts(tool.test) is False
        assert tool.should_pass_artifacts(tool.test_with_required_ramp) is True
