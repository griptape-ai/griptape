from __future__ import annotations
from typing import Optional
from attr import define, field
from skatepark.tools import Tool
from skatepark.steps import BaseToolStep


@define
class ToolStep(BaseToolStep):
    tool: Tool = field(kw_only=True)

    def find_tool(self, tool_name: str) -> Optional[Tool]:
        if self.tool.name == tool_name:
            return self.tool
        else:
            return None
