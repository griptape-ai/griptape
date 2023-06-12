from attr import define, field
from schema import Schema, Literal
from griptape.artifacts import TextArtifact, ErrorArtifact, BaseArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity


@define
class MockTool(BaseTool):
    test_field: str = field(default="test", kw_only=True)
    test_int: int = field(default=5, kw_only=True)
    test_dict: dict = field(factory=dict, kw_only=True)

    @activity(config={
        "description": "test description: {{ foo }}",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        )
    })
    def test(self, value: dict) -> BaseArtifact:
        return TextArtifact(f"ack {value['test']}")

    @activity(config={
        "description": "test description: {{ foo }}",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        )
    })
    def test_error(self, value: dict) -> BaseArtifact:
        return ErrorArtifact(f"error {value['test']}")

    @activity(config={
        "description": "test description: {{ foo }}",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        )
    })
    def test_str_output(self, value: dict) -> str:
        return f"ack {value['test']}"

    @activity(config={
        "description": "test description"
    })
    def test_no_schema(self) -> str:
        return f"no schema"

    @activity(config={
        "description": "test description",
        "schema": Schema({
                Literal("test"): str
            },
            description="Test input"
        ),
        "load_artifacts": True
    })
    def test_with_required_memory(self, value: dict) -> str:
        return f"ack {value['test']}"

    @property
    def schema_template_args(self) -> dict:
        return {
            "foo": "bar"
        }
