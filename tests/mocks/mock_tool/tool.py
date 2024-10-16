from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class MockTool(BaseTool):
    test_field: str = field(default="test", kw_only=True)
    test_int: int = field(default=5, kw_only=True)
    test_dict: dict = field(factory=dict, kw_only=True)
    custom_schema: dict = field(default=Factory(lambda: {"test": str}), kw_only=True)
    module_name: str = field(
        default=Factory(lambda self: self.__class__.__module__, takes_self=True),
        kw_only=True,
        metadata={"serializable": False},
    )

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test(self, **kwargs) -> BaseArtifact:
        return TextArtifact(f"ack {kwargs['test']}")

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test_error(self, params: dict) -> BaseArtifact:
        return ErrorArtifact(f"error {params['values']['test']}")

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test_exception(self, params: dict) -> BaseArtifact:
        raise Exception(f"error {params['values']['test']}")

    @activity(
        config={
            "description": "test description: {{ _self.foo() }}",
            "schema": Schema({Literal("test"): str}, description="Test input"),
        }
    )
    def test_str_output(self, params: dict) -> str:
        return f"ack {params['values']['test']}"

    @activity(config={"description": "test description"})
    def test_no_schema(self) -> str:
        return "no schema"

    @activity(
        config={
            "description": "test description",
            "schema": lambda _self: _self.build_custom_schema(),
        }
    )
    def test_callable_schema(self) -> TextArtifact:
        return TextArtifact("ack")

    @activity(config={"description": "test description"})
    def test_list_output(self) -> ListArtifact:
        return ListArtifact([TextArtifact("foo"), TextArtifact("bar")])

    @activity(
        config={"description": "test description", "schema": Schema({Literal("test"): str}, description="Test input")}
    )
    def test_without_default_memory(self, params: dict) -> str:
        return f"ack {params['values']['test']}"

    def foo(self) -> str:
        return "foo"

    def build_custom_schema(self) -> Schema:
        return Schema(self.custom_schema, description="Test input")
