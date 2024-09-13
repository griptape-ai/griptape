import json

import pytest

from griptape.artifacts import ActionArtifact, BaseArtifact
from griptape.common import ToolAction


class TestActionArtifact:
    @pytest.fixture()
    def action(self) -> ToolAction:
        return ToolAction(tag="TestTag", name="TestName", path="TestPath", input={"foo": "bar"})

    def test_to_text(self, action):
        assert ActionArtifact(action).to_text() == json.dumps(action.to_dict())

    def test_to_dict(self, action):
        assert ActionArtifact(action).to_dict()["value"] == {
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
            "type": "ToolAction",
        }

    def test_from_dict(self, action):
        assert BaseArtifact.from_dict(ActionArtifact(action).to_dict()).to_dict()["value"] == {
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
            "type": "ToolAction",
        }

    def test_to_json(self, action):
        assert json.loads(ActionArtifact(action).to_json())["value"] == {
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
            "type": "ToolAction",
        }

    def test_from_json(self, action):
        assert ActionArtifact.from_json(ActionArtifact(action).to_json()).to_dict()["value"] == {
            "tag": "TestTag",
            "name": "TestName",
            "path": "TestPath",
            "input": {"foo": "bar"},
            "type": "ToolAction",
        }
