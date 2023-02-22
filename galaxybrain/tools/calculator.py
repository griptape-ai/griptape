from galaxybrain.tools import Tool
from galaxybrain.utils import J2, PythonRunner


class Calculator(Tool):
    def name(self) -> str:
        return "calculator"

    def description(self) -> str:
        return "This tool is capable of performing any calculation in Python syntax"

    def examples(self) -> str:
        return J2("tools/calculator/examples.j2").render()

    def run(self, value: str) -> str:
        return PythonRunner().run(f"print({value})")
