from attrs import define
from schema import Literal, Schema

from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class MockToolKwargs(BaseTool):
    @activity(
        config={
            "description": "test description",
            "schema": Schema({Literal("test_kwarg"): str}, description="Test input"),
        }
    )
    def test_with_kwargs(self, params: dict, test_kwarg: str, test_kwarg_none: None, **kwargs) -> str:
        if test_kwarg_none is not None:
            raise ValueError("test_kwarg_none should be None")
        if "test_kwarg_kwargs" not in kwargs:
            raise ValueError("test_kwarg_kwargs not in kwargs")
        if "values" not in kwargs:
            raise ValueError("values not in params")
        if "test_kwarg" not in params["values"]:
            raise ValueError("test_kwarg not in params")
        return f"ack {test_kwarg}"
