from attrs import define
from warpspeed.tools import Tool
from warpspeed.utils import PythonRunner


@define
class CalculatorTool(Tool):
    def run(self, value: str) -> str:
        return PythonRunner().run(value)
