from __future__ import annotations
from typing import Optional
from attr import define, field
from griptape.core import BaseTool
from skatepark.steps import BaseToolStep


@define
class ToolStep(BaseToolStep):
    tool_name: str = field(kw_only=True)

    @property
    def tool(self) -> Optional[BaseTool]:
        return self.structure.tool_loader.load_tool(self.tool_name)

    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        if self.tool_name == tool_name:
            return self.tool
        else:
            return None
