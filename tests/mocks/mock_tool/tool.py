from attr import define, field
from schema import Schema
from griptape.artifacts import TextArtifact, ErrorArtifact, BaseArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity


@define
class MockTool(BaseTool):
    test_field: str = field(default="test", kw_only=True, metadata={"env": "TEST_FIELD"})
    test_int: int = field(default=5, kw_only=True, metadata={"env": "TEST_INT"})

    @activity(config={
        "name": "test",
        "description": "test description: {{ foo }}",
        "schema": Schema(
            str,
            description="Test input"
        ),
        "foo": "bar"
    })
    def test(self, value: str) -> BaseArtifact:
        return TextArtifact(f"ack {value}")

    @activity(config={
        "name": "test_error",
        "description": "test description: {{ foo }}",
        "schema": Schema(
            str,
            description="Test input"
        ),
        "foo": "bar"
    })
    def test_error(self, value: str) -> BaseArtifact:
        return ErrorArtifact(f"error {value}")

    @activity(config={
        "name": "test_str_output",
        "description": "test description: {{ foo }}",
        "schema": Schema(
            str,
            description="Test input"
        ),
        "foo": "bar"
    })
    def test_str_output(self, value: str) -> str:
        return f"ack {value}"

    @property
    def schema_template_args(self) -> dict:
        return {
            "foo": "bar"
        }
