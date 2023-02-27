from galaxybrain.tools import Tool
from galaxybrain.utils import PythonRunner


class Calculator(Tool):
    def run(self, value: str) -> str:
        return PythonRunner().run(value)
