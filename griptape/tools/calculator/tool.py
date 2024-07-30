from schema import Literal, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


class Calculator(BaseTool):
    @activity(
        config={
            "description": "Can be used for computing simple numerical or algebraic calculations in Python",
            "schema": Schema(
                {
                    Literal(
                        "expression",
                        description="Arithmetic expression parsable in pure Python. Single line only. "
                        "Don't use variables. Don't use any imports or external libraries",
                    ): str,
                },
            ),
        },
    )
    def calculate(self, params: dict) -> BaseArtifact:
        import numexpr  # pyright: ignore[reportMissingImports]

        try:
            expression = params["values"]["expression"]

            return TextArtifact(numexpr.evaluate(expression))
        except Exception as e:
            return ErrorArtifact(f"error calculating: {e}")
