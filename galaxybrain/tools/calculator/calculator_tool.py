from attrs import define
from galaxybrain.tools import Tool
from galaxybrain.utils import PythonRunner


@define(frozen=True)
class CalculatorTool(Tool):
    def run(self, value: str) -> str:
        return PythonRunner().run(value)
