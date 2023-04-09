from attr import define
from skatepark.tools import Tool
from skatepark.utils import PythonRunner


@define
class CalculatorTool(Tool):
    def run(self, value: str) -> str:
        return PythonRunner().run(value)
