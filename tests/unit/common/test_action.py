import pytest
import json
from griptape.common import Action


class TestAction:
    @pytest.fixture()
    def action(self) -> Action:
        return Action(tag="TestTag", name="TestName", path="TestPath", input={"foo": "bar"})

    def test__str__(self, action: Action):
        assert str(action) == json.dumps(
            {"type": "Action", "tag": "TestTag", "name": "TestName", "path": "TestPath", "input": {"foo": "bar"}}
        )

    def test_to_dict(self, action: Action):
        assert action.to_dict() == {
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
            "type": "Action",
        }

    def test_to_native_tool_name(self, action: Action):
        assert action.to_native_tool_name() == "TestName_TestPath"

        action.path = None
        assert action.to_native_tool_name() == "TestName"

    def test_from_native_tool_name(self):
        assert Action.from_native_tool_name("TestName_TestPath") == ("TestName", "TestPath")
        assert Action.from_native_tool_name("TestName") == ("TestName", None)
