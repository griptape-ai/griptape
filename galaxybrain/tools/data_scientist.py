from galaxybrain.tools import Tool
from galaxybrain.utils import J2, PythonRunner


class DataScientist(Tool):
    AVAILABLE_LIBRARIES = {"numpy": "np", "math": "math"}

    def __init__(self):
        self.description =\
            f"This tool is capable of executing Python code with the following imports: {self.__imports()}"
        self.examples =\
            J2("tools/data_scientist/examples.j2").render()

    def run(self, value: str) -> str:
        return PythonRunner(libs=self.AVAILABLE_LIBRARIES).run(f"print({value})")

    def __imports(self):
        return str.join(", ", self.AVAILABLE_LIBRARIES.values())
