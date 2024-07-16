import json

import pytest

from griptape.common import ToolAction


class TestAction:
    @pytest.fixture()
    def action(self) -> ToolAction:
        return ToolAction(tag="TestTag", name="TestName", path="TestPath", input={"foo": "bar"})

    def test__str__(self, action: ToolAction):
        assert str(action) == json.dumps(
            {"type": "ToolAction", "tag": "TestTag", "name": "TestName", "path": "TestPath", "input": {"foo": "bar"}}
        )

    def test_to_dict(self, action: ToolAction):
        assert action.to_dict() == {
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
            "type": "ToolAction",
        }

    def test_to_native_tool_name(self, action: ToolAction):
        assert action.to_native_tool_name() == "TestName_TestPath"

        action.path = None
        assert action.to_native_tool_name() == "TestName"

    def test_from_native_tool_name(self):
        assert ToolAction.from_native_tool_name("TestName_TestPath") == ("TestName", "TestPath")
        assert ToolAction.from_native_tool_name("TestName") == ("TestName", None)
