from typing import Optional
from attrs import define, field
from warpspeed.tools import Tool
from warpspeed.steps import BaseToolStep


@define
class ToolkitStep(BaseToolStep):
    tools: list[Tool] = field(kw_only=True)

    def find_tool(self, action_name: str) -> Optional[Tool]:
        for tool in self.tools:
            if tool.name == action_name:
                return tool

        return None
