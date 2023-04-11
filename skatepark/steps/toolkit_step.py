from attr import define, field
from griptape.core import BaseTool
from skatepark.steps import BaseToolStep


@define
class ToolkitStep(BaseToolStep):
    tool_names: list[str] = field(kw_only=True)

    @property
    def tools(self) -> list[BaseTool]:
        return [
            t for t in [self.structure.tool_loader.load_tool(t) for t in self.tool_names] if t is not None
        ]