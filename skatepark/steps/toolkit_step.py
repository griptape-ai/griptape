from typing import Optional
from attr import define, field
from skatepark.tools import Tool
from skatepark.steps import BaseToolStep


@define
class ToolkitStep(BaseToolStep):
    tools: list[Tool] = field(kw_only=True)

    def find_tool(self, tool_name: str) -> Optional[Tool]:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool

        return None
