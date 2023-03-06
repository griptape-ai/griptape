from attrs import define
from warpspeed.tools import Tool
from warpspeed.utils import PythonRunner


@define(frozen=True)
class DataScientistTool(Tool):
    AVAILABLE_LIBRARIES = {"numpy": "np", "math": "math"}

    def run(self, value: str) -> str:
        return PythonRunner(libs=self.AVAILABLE_LIBRARIES).run(value)

    @property
    def schema_kwargs(self) -> dict:
        return {
            "imports": self.__imports()
        }

    def __imports(self):
        return str.join(", ", self.AVAILABLE_LIBRARIES.values())
