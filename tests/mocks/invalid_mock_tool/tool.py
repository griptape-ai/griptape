from typing import Any

from attrs import define, field
from schema import Literal, Schema

from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class InvalidMockTool(BaseTool):
    configs = {
        "test": {
            # no description should make this tool invalid
            "schema": Schema({Literal("input", description="Test input"): str}),
            "foo": "bar",
        }
    }

    test_field: str = field(default="test", kw_only=True, metadata={"env": "TEST_FIELD"})

    @activity(config=configs["test"])
    def test(self, value: Any) -> str:
        return f"ack {value}"
