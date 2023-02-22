from galaxybrain.tools import Tool
from galaxybrain.utils import J2, PythonRunner


class Calculator(Tool):
    def __init__(self):
        self.name = "calculator"
        self.description =\
            "This tool is capable of performing any calculation in Python syntax"
        self.examples =\
            J2("tools/calculator/examples.j2").render()

    def run(self, value: str) -> str:
        return PythonRunner().run(f"print({value})")
