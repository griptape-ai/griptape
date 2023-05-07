from attr import define, field
from schema import Schema, Literal
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
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        ),
        "foo": "bar"
    })
    def test(self, value: str) -> BaseArtifact:
        return TextArtifact(f"ack {value}")

    @activity(config={
        "name": "test_error",
        "description": "test description: {{ foo }}",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        ),
        "foo": "bar"
    })
    def test_error(self, value: str) -> BaseArtifact:
        return ErrorArtifact(f"error {value}")

    @activity(config={
        "name": "test_str_output",
        "description": "test description: {{ foo }}",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        ),
        "foo": "bar"
    })
    def test_str_output(self, value: str) -> str:
        return f"ack {value}"

    @activity(config={
        "name": "test_no_schema",
        "description": "test description"
    })
    def test_no_schema(self) -> str:
        return f"no schema"

    @activity(config={
        "name": "test_with_required_ramp",
        "description": "test description",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        ),
        "pass_artifact": True
    })
    def test_with_required_ramp(self, value: str) -> str:
        return f"ack {value}"

    @property
    def schema_template_args(self) -> dict:
        return {
            "foo": "bar"
        }
