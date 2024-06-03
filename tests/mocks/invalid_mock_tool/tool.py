from attrs import define, field
from schema import Schema, Literal
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class InvalidMockTool(BaseTool):
    configs = {
        "test": {
            # no description should make this tool invalid
            # "description": "test description",
            "schema": Schema({Literal("input", description="Test input"): str}),
            "foo": "bar",
        }
    }

    test_field: str = field(default="test", kw_only=True, metadata={"env": "TEST_FIELD"})

    @activity(config=configs["test"])
    def test(self, value: any) -> str:
        return f"ack {value}"
