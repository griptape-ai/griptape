from typing import Optional
from attr import define, field
from griptape.core import BaseTool
from skatepark.steps import BaseToolStep


@define
class ToolkitStep(BaseToolStep):
    tool_names: list[str] = field(kw_only=True)

    @property
    def tools(self) -> list[BaseTool]:
        return [self.structure.tool_loader.load_tool(t) for t in self.tool_names]

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        return next(
            (t for t in self.tools if t.name == tool_name),
            None
        )
