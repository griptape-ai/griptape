from attr import define, field
from schema import Schema
from griptape.core import BaseTool
from griptape.utils import action


@define
class MockTool(BaseTool):
    configs = {
        "test": {
            "name": "test",
            "description": "test description: {{ foo }}",
            "schema": Schema(
                str,
                description="Test input"
            ),
            "foo": "bar"
        }
    }

    test_field: str = field(default="test", kw_only=True, metadata={"env": "TEST_FIELD"})
    test_int: int = field(default=5, kw_only=True, metadata={"env": "TEST_INT"})

    @action(config=configs["test"])
    def test(self, value: bytes) -> str:
        return f"ack {value.decode()}"

    @property
    def schema_template_args(self) -> dict:
        return {
            "foo": "bar"
        }
