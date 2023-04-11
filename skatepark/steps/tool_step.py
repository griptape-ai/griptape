from __future__ import annotations
from attr import define, field
from griptape.core import BaseTool
from skatepark.steps import BaseToolStep


@define
class ToolStep(BaseToolStep):
    tool_name: str = field(kw_only=True)

    @property
    def tools(self) -> list[BaseTool]:
        tool = self.structure.tool_loader.load_tool(self.tool_name)

        return [tool] if tool else []
