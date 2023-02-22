from galaxybrain.tools import Tool
from galaxybrain.utils import J2, PythonRunner


class DataScientist(Tool):
    AVAILABLE_LIBRARIES = {"numpy": "np", "math": "math"}
    def description(self) -> str:
        return f"This tool is capable of executing Python code with the following imports: {self.__imports()}"

    def examples(self) -> str:
        return J2("tools/data_scientist/examples.j2").render()

    def run(self, value: str) -> str:
        return PythonRunner(libs=self.AVAILABLE_LIBRARIES).run(f"print({value})")

    def __imports(self):
        return str.join(", ", self.AVAILABLE_LIBRARIES.values())