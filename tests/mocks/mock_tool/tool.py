from attrs import define, field
from schema import Schema, Literal
from griptape.artifacts import TextArtifact, ErrorArtifact, BaseArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class MockTool(BaseTool):
    test_field: str = field(default="test", kw_only=True)
    test_int: int = field(default=5, kw_only=True)
    test_dict: dict = field(factory=dict, kw_only=True)

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test(self, value: dict) -> BaseArtifact:
        return TextArtifact(f"ack {value['values']['test']}")

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test_error(self, value: dict) -> BaseArtifact:
        return ErrorArtifact(f"error {value['values']['test']}")

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test_str_output(self, value: dict) -> str:
        return f"ack {value['values']['test']}"

    @activity(config={"description": "test description"})
    def test_no_schema(self, value: dict) -> str:
        return f"no schema"

    @activity(config={"description": "test description"})
    def test_list_output(self, value: dict) -> ListArtifact:
        return ListArtifact([TextArtifact("foo"), TextArtifact("bar")])

    @activity(
        config={"description": "test description", "schema": Schema({Literal("test"): str}, description="Test input")}
    )
    def test_without_default_memory(self, value: dict) -> str:
        return f"ack {value['values']['test']}"

    def foo(self) -> str:
        return "foo"
