from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal


class Calculator(BaseTool):
    @activity(
        config={
            "description": "Can be used for making simple numeric or algebraic calculations in Python",
            "schema": Schema(
                {
                    Literal(
                        "expression",
                        description="Arithmetic expression parsable in pure Python. Single line only. Don't use any "
                        "imports or external libraries",
                    ): str
                }
            ),
        }
    )
    def calculate(self, params: dict) -> BaseArtifact:
        import numexpr

        try:
            expression = params["values"]["expression"]

            return TextArtifact(numexpr.evaluate(expression))
        except Exception as e:
            return ErrorArtifact(f"error calculating: {e}")
