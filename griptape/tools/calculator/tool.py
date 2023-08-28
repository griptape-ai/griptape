from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
import griptape.utils as utils
from schema import Schema, Literal


class Calculator(BaseTool):
    @activity(config={
        "description": "Can be used for making simple numeric or algebraic calculations in Python",
        "uses_default_memory": False,
        "schema": Schema({
            Literal(
                "expression",
                description="Arithmetic expression parsable in pure Python. Single line only. Don't use any "
                            "imports or external libraries"
            ): str
        })
    })
    def calculate(self, params: dict) -> BaseArtifact:
        try:
            expression = params["values"]["expression"]

            return TextArtifact(utils.PythonRunner().run(expression))
        except Exception as e:
            return ErrorArtifact(f"error calculating: {e}")
